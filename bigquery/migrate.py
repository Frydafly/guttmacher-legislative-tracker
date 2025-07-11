#!/usr/bin/env python3
"""
GUTTMACHER LEGISLATIVE TRACKER - HISTORICAL DATA MIGRATION
==========================================================

Single script for complete migration of historical legislative data (2005-2024).
Handles database evolution, schema harmonization, and Looker Studio table creation.

Usage:
    python migrate.py                    # Run full migration
    python migrate.py --test             # Test migration results
    python migrate.py --cleanup          # Clean up old objects
    python migrate.py --looker-only      # Create just Looker table

Prerequisites:
    1. brew install mdbtools
    2. pip install -r requirements.txt  
    3. gcloud auth application-default login
    4. Configure .env file with GCP_PROJECT_ID
    5. Copy .mdb/.accdb files to ./data/
"""

import argparse
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud import exceptions as google_exceptions


class GuttmacherMigration:
    """Complete historical data migration pipeline."""

    def __init__(self):
        """Initialize the migration."""
        load_dotenv()
        
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = "legislative_tracker_historical"
        
        if not self.project_id or self.project_id == "your-actual-project-id":
            raise ValueError("Please set GCP_PROJECT_ID in .env file")
        
        self.bq_client = bigquery.Client(project=self.project_id)
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        
        # Load field mappings
        self.field_mappings = self._load_field_mappings()
        
        # Migration statistics
        self.stats = {
            "start_time": datetime.now(),
            "files_processed": 0,
            "total_bills": 0,
            "years_processed": [],
            "errors": [],
            "field_mappings_applied": 0
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.base_path / "migration.log", mode="a")
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_field_mappings(self) -> Dict[str, Any]:
        """Load field mappings configuration."""
        mappings_path = self.base_path / "field_mappings.yaml"
        if not mappings_path.exists():
            raise FileNotFoundError(f"Field mappings file not found: {mappings_path}")
        
        with open(mappings_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_reverse_mapping(self) -> Dict[str, str]:
        """Create reverse mapping from original field names to standardized names."""
        reverse_map = {}
        for category_name, category_fields in self.field_mappings.items():
            if category_name in ['table_patterns', 'bigquery_types']:
                continue
            if isinstance(category_fields, dict):
                for standard_name, variants in category_fields.items():
                    if isinstance(variants, list):
                        for variant in variants:
                            reverse_map[variant] = standard_name
        return reverse_map

    def validate_setup(self) -> bool:
        """Validate migration prerequisites."""
        self.logger.info("🔍 Validating migration setup...")
        
        # Check mdbtools
        try:
            result = subprocess.run(["mdb-tables", "--help"], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                self.logger.error("❌ mdbtools not working. Install: brew install mdbtools")
                return False
            self.logger.info("✅ mdbtools available")
        except FileNotFoundError:
            self.logger.error("❌ mdbtools not found. Install: brew install mdbtools")
            return False

        # Check BigQuery access
        try:
            list(self.bq_client.list_datasets(max_results=1))
            self.logger.info("✅ BigQuery access confirmed")
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("❌ BigQuery access failed: %s", e)
            return False

        # Create dataset if needed
        try:
            self.bq_client.get_dataset(self.dataset_id)
            self.logger.info("✅ Dataset '%s' exists", self.dataset_id)
        except google_exceptions.NotFound:
            try:
                dataset = bigquery.Dataset(f"{self.project_id}.{self.dataset_id}")
                dataset.location = "US"
                self.bq_client.create_dataset(dataset)
                self.logger.info("✅ Created dataset '%s'", self.dataset_id)
            except google_exceptions.GoogleCloudError as e:
                self.logger.error("❌ Failed to create dataset: %s", e)
                return False

        # Check for database files
        db_files = list(self.data_path.glob("*.mdb")) + list(self.data_path.glob("*.accdb"))
        if not db_files:
            self.logger.error("❌ No database files found in %s", self.data_path)
            return False

        self.logger.info("✅ Found %d database files for migration", len(db_files))
        self.logger.info("✅ Field mappings loaded")
        return True

    def extract_year_from_filename(self, db_path: Path) -> Optional[int]:
        """Extract year from database filename."""
        patterns = [r"(\d{4})", r"\b(\d{2})-\d{2}-(\d{2})\b"]
        for pattern in patterns:
            match = re.search(pattern, db_path.name)
            if match:
                year_str = match.group(1)
                year = int(year_str)
                if len(year_str) == 2:
                    year = year + 2000 if year <= 30 else year + 1900
                if 2000 <= year <= 2030:
                    return year
        return None

    def get_tables_from_db(self, db_path: Path) -> List[str]:
        """Get list of tables from database file."""
        try:
            result = subprocess.run(["mdb-tables", "-1", str(db_path)], 
                                  capture_output=True, text=True, timeout=30, check=False)
            if result.returncode != 0:
                return []
            return [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        except subprocess.TimeoutExpired:
            return []

    def find_primary_table(self, tables: List[str]) -> Optional[str]:
        """Find the primary legislative monitoring table."""
        patterns = [r".*Legislative.*Monitoring.*", r".*Monitoring.*Table.*", r".*State.*Legislative.*Table.*"]
        for pattern in patterns:
            for table in tables:
                if re.match(pattern, table, re.IGNORECASE):
                    return table
        return tables[0] if tables else None

    def export_table_to_dataframe(self, db_path: Path, table: str) -> Optional[pd.DataFrame]:
        """Export table to DataFrame."""
        try:
            result = subprocess.run(["mdb-export", str(db_path), table],
                                  capture_output=True, text=True, timeout=120, check=False)
            if result.returncode == 0 and result.stdout.strip():
                from io import StringIO
                df = pd.read_csv(StringIO(result.stdout), low_memory=False)
                return None if df.empty else df
            return None
        except Exception:
            return None

    def harmonize_schema(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """Harmonize DataFrame schema using field mappings."""
        if df.empty:
            return df
            
        reverse_map = self._create_reverse_mapping()
        standardized_data = {}
        
        # Get all possible standardized fields
        all_standard_fields = set()
        for category in self.field_mappings.values():
            if isinstance(category, dict):
                all_standard_fields.update(category.keys())
        all_standard_fields.discard('table_patterns')
        all_standard_fields.discard('bigquery_types')
        
        # Initialize fields with appropriate defaults
        # Status fields should default to FALSE, category fields should default to NULL
        status_fields = {
            'introduced', 'seriously_considered', 'passed_first_chamber', 
            'passed_second_chamber', 'enacted', 'vetoed', 'dead', 'pending'
        }
        
        for field in all_standard_fields:
            field_type = self.field_mappings.get('bigquery_types', {}).get(field, 'STRING')
            if field_type == 'BOOLEAN':
                if field in status_fields:
                    standardized_data[field] = False  # Status fields default to FALSE
                else:
                    standardized_data[field] = None   # Category fields default to NULL when not tracked
            else:
                standardized_data[field] = None
        
        # Map existing columns
        mapped_count = 0
        for original_col in df.columns:
            if original_col in reverse_map:
                standard_name = reverse_map[original_col]
                standardized_data[standard_name] = df[original_col]
                mapped_count += 1
                
        # Add metadata
        standardized_data['data_year'] = year
        standardized_data['migration_date'] = date.today()
        standardized_data['data_source'] = "Historical Migration"
        
        # Create DataFrame with consistent length
        if len(df) > 0:
            for key, value in standardized_data.items():
                if not isinstance(value, pd.Series):
                    standardized_data[key] = [value] * len(df)
        
        self.stats['field_mappings_applied'] += mapped_count
        return pd.DataFrame(standardized_data)

    def clean_dataframe_for_bigquery(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for BigQuery compatibility."""
        if df.empty:
            return df
            
        df_clean = df.copy()
        
        # Clean column names
        df_clean.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", str(col)).strip("_").lower() 
                           for col in df_clean.columns]
        
        # Handle date fields
        date_fields = ['last_action_date', 'introduced_date', 'enacted_date', 'vetoed_date']
        for col in date_fields:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

        datetime_fields = ['date_last_updated']
        for col in datetime_fields:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

        # Clean string fields (force bill_number to string regardless of input type)
        string_fields = ['state', 'bill_type', 'bill_number', 'description', 'history', 'notes', 
                        'website_blurb', 'internal_summary', 'data_source', 'effective_date']
        
        # Add all topic fields to string fields
        topic_fields = [f'topic_{i}' for i in range(1, 11)]
        string_fields.extend(topic_fields)
        
        for col in string_fields:
            if col in df_clean.columns:
                # Always convert to string, handling float64 NaN properly
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(['nan', 'None', ''], None)

        # Ensure boolean fields
        boolean_fields = [k for k, v in self.field_mappings.get('bigquery_types', {}).items() 
                         if v == 'BOOLEAN']
        for col in boolean_fields:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(bool)

        return df_clean

    def load_to_bigquery(self, df: pd.DataFrame, table_name: str) -> bool:
        """Load DataFrame to BigQuery."""
        if df.empty:
            return False

        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        # Create schema
        schema = []
        for col in df.columns:
            bq_type = self.field_mappings.get('bigquery_types', {}).get(col, 'STRING')
            schema.append(bigquery.SchemaField(col, bq_type))

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            schema=schema,
            create_disposition="CREATE_IF_NEEDED"
        )

        try:
            job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result(timeout=300)
            self.logger.info("✅ Loaded %d rows to %s", len(df), table_name)
            return True
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("❌ Failed to load %s: %s", table_name, e)
            return False

    def process_db_file(self, db_path: Path) -> bool:
        """Process a single database file."""
        year = self.extract_year_from_filename(db_path)
        if not year:
            return False

        self.logger.info("📁 Processing %s (%d)", db_path.name, year)
        
        tables = self.get_tables_from_db(db_path)
        if not tables:
            self.logger.error("No tables found in %s", db_path.name)
            return False

        primary_table = self.find_primary_table(tables)
        if not primary_table:
            self.logger.error("Could not identify primary table in %s", db_path.name)
            return False

        df = self.export_table_to_dataframe(db_path, primary_table)
        if df is None or df.empty:
            self.logger.error("Failed to export primary table from %s", db_path.name)
            return False

        try:
            df_harmonized = self.harmonize_schema(df, year)
            df_clean = self.clean_dataframe_for_bigquery(df_harmonized)
            
            table_name = f"historical_bills_{year}"
            if self.load_to_bigquery(df_clean, table_name):
                self.stats["files_processed"] += 1
                self.stats["years_processed"].append(year)
                self.stats["total_bills"] += len(df_clean)
                return True
        except Exception as e:
            self.logger.error("Error processing %s: %s", db_path.name, e)
            self.stats["errors"].append(f"{db_path.name}: {e}")

        return False

    def create_unified_view(self):
        """Create unified view and table of all historical data."""
        self.logger.info("🔗 Creating unified historical view and table...")
        
        query = f"""
        SELECT table_name FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`
        WHERE table_name LIKE 'historical_bills_%' ORDER BY table_name
        """
        
        try:
            results = self.bq_client.query(query).result()
            tables = [row.table_name for row in results]
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to list tables: %s", e)
            return

        if not tables:
            return

        union_parts = [f"SELECT * FROM `{self.project_id}.{self.dataset_id}.{table}`" for table in tables]
        
        # Create view first (for compatibility)
        create_view_sql = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.all_historical_bills_unified` AS
        {' UNION ALL '.join(union_parts)}
        """

        try:
            job = self.bq_client.query(create_view_sql)
            job.result()
            self.logger.info("✅ Created unified view: all_historical_bills_unified")
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to create unified view: %s", e)
            return
            
        # Create materialized table for better Looker performance
        create_table_sql = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.all_historical_bills_materialized` 
        CLUSTER BY (state, data_year) AS
        {' UNION ALL '.join(union_parts)}
        """

        try:
            job = self.bq_client.query(create_table_sql)
            job.result(timeout=600)  # Longer timeout for large table creation
            self.logger.info("✅ Created materialized table: all_historical_bills_materialized")
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to create materialized table: %s", e)

    def create_looker_table(self):
        """Create authentic comprehensive view that preserves NULL patterns."""
        self.logger.info("🔄 Creating authentic comprehensive view...")
        
        create_table_sql = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.comprehensive_bills_authentic` AS
        WITH enhanced_bills AS (
          SELECT 
            id,
            CONCAT(state, '-', bill_number, '-', data_year) as unique_bill_key,
            data_year,
            CAST(data_year AS STRING) as data_year_str,
            state as state_code,
            CASE state
              WHEN 'AL' THEN 'Alabama' WHEN 'AK' THEN 'Alaska' WHEN 'AZ' THEN 'Arizona'
              WHEN 'AR' THEN 'Arkansas' WHEN 'CA' THEN 'California' WHEN 'CO' THEN 'Colorado'
              WHEN 'CT' THEN 'Connecticut' WHEN 'DE' THEN 'Delaware' WHEN 'FL' THEN 'Florida'
              WHEN 'GA' THEN 'Georgia' WHEN 'HI' THEN 'Hawaii' WHEN 'ID' THEN 'Idaho'
              WHEN 'IL' THEN 'Illinois' WHEN 'IN' THEN 'Indiana' WHEN 'IA' THEN 'Iowa'
              WHEN 'KS' THEN 'Kansas' WHEN 'KY' THEN 'Kentucky' WHEN 'LA' THEN 'Louisiana'
              WHEN 'ME' THEN 'Maine' WHEN 'MD' THEN 'Maryland' WHEN 'MA' THEN 'Massachusetts'
              WHEN 'MI' THEN 'Michigan' WHEN 'MN' THEN 'Minnesota' WHEN 'MS' THEN 'Mississippi'
              WHEN 'MO' THEN 'Missouri' WHEN 'MT' THEN 'Montana' WHEN 'NE' THEN 'Nebraska'
              WHEN 'NV' THEN 'Nevada' WHEN 'NH' THEN 'New Hampshire' WHEN 'NJ' THEN 'New Jersey'
              WHEN 'NM' THEN 'New Mexico' WHEN 'NY' THEN 'New York' WHEN 'NC' THEN 'North Carolina'
              WHEN 'ND' THEN 'North Dakota' WHEN 'OH' THEN 'Ohio' WHEN 'OK' THEN 'Oklahoma'
              WHEN 'OR' THEN 'Oregon' WHEN 'PA' THEN 'Pennsylvania' WHEN 'RI' THEN 'Rhode Island'
              WHEN 'SC' THEN 'South Carolina' WHEN 'SD' THEN 'South Dakota' WHEN 'TN' THEN 'Tennessee'
              WHEN 'TX' THEN 'Texas' WHEN 'UT' THEN 'Utah' WHEN 'VT' THEN 'Vermont'
              WHEN 'VA' THEN 'Virginia' WHEN 'WA' THEN 'Washington' WHEN 'WV' THEN 'West Virginia'
              WHEN 'WI' THEN 'Wisconsin' WHEN 'WY' THEN 'Wyoming'
              ELSE state
            END as state_name,
            
            CASE state
              WHEN 'CT' THEN 'Northeast' WHEN 'ME' THEN 'Northeast' WHEN 'MA' THEN 'Northeast'
              WHEN 'NH' THEN 'Northeast' WHEN 'NJ' THEN 'Northeast' WHEN 'NY' THEN 'Northeast'
              WHEN 'PA' THEN 'Northeast' WHEN 'RI' THEN 'Northeast' WHEN 'VT' THEN 'Northeast'
              WHEN 'IL' THEN 'Midwest' WHEN 'IN' THEN 'Midwest' WHEN 'IA' THEN 'Midwest'
              WHEN 'KS' THEN 'Midwest' WHEN 'MI' THEN 'Midwest' WHEN 'MN' THEN 'Midwest'
              WHEN 'MO' THEN 'Midwest' WHEN 'NE' THEN 'Midwest' WHEN 'ND' THEN 'Midwest'
              WHEN 'OH' THEN 'Midwest' WHEN 'SD' THEN 'Midwest' WHEN 'WI' THEN 'Midwest'
              WHEN 'AL' THEN 'South' WHEN 'AR' THEN 'South' WHEN 'DE' THEN 'South'
              WHEN 'FL' THEN 'South' WHEN 'GA' THEN 'South' WHEN 'KY' THEN 'South'
              WHEN 'LA' THEN 'South' WHEN 'MD' THEN 'South' WHEN 'MS' THEN 'South'
              WHEN 'NC' THEN 'South' WHEN 'OK' THEN 'South' WHEN 'SC' THEN 'South'
              WHEN 'TN' THEN 'South' WHEN 'TX' THEN 'South' WHEN 'VA' THEN 'South'
              WHEN 'WV' THEN 'South'
              ELSE 'West'
            END as region,
            
            CASE 
              WHEN data_year BETWEEN 2005 AND 2009 THEN '2005-2009'
              WHEN data_year BETWEEN 2010 AND 2014 THEN '2010-2014'
              WHEN data_year BETWEEN 2015 AND 2019 THEN '2015-2019'
              WHEN data_year BETWEEN 2020 AND 2024 THEN '2020-2024'
              ELSE 'Other'
            END as time_period,
            
            bill_type, bill_number, description, history, notes, website_blurb, internal_summary,
            last_action_date, introduced_date, enacted_date, vetoed_date, date_last_updated, effective_date,
            
            DATE_DIFF(enacted_date, introduced_date, DAY) as days_to_enactment,
            DATE_DIFF(last_action_date, introduced_date, DAY) as days_since_introduction,
            
            introduced, seriously_considered, passed_first_chamber, passed_second_chamber,
            enacted, vetoed, dead, pending, positive, neutral, restrictive,
            
            CASE 
              WHEN enacted = TRUE THEN 'Enacted'
              WHEN vetoed = TRUE THEN 'Vetoed'
              WHEN dead = TRUE THEN 'Dead'
              WHEN pending = TRUE THEN 'Pending'
              WHEN passed_second_chamber = TRUE THEN 'Passed Both Chambers'
              WHEN passed_first_chamber = TRUE THEN 'Passed One Chamber'
              WHEN seriously_considered = TRUE THEN 'Seriously Considered'
              WHEN introduced = TRUE THEN 'Introduced'
              ELSE 'Unknown'
            END AS status_category,
            
            CASE
              WHEN positive = TRUE THEN 'Positive'
              WHEN neutral = TRUE THEN 'Neutral' 
              WHEN restrictive = TRUE THEN 'Restrictive'
              ELSE 'Unclassified'
            END AS intent,
            
            abortion, contraception, emergency_contraception, minors, pregnancy, refusal, sex_education,
            insurance, appropriations, fetal_issues, fetal_tissue, incarceration, period_products, stis,
            legislation, resolution, ballot_initiative, constitutional_amendment, court_case,
            
            (CAST(abortion AS INT64) + CAST(contraception AS INT64) + CAST(emergency_contraception AS INT64) +
             CAST(minors AS INT64) + CAST(pregnancy AS INT64) + CAST(refusal AS INT64) + CAST(sex_education AS INT64) +
             CAST(insurance AS INT64) + CAST(appropriations AS INT64) + CAST(fetal_issues AS INT64) +
             CAST(fetal_tissue AS INT64) + CAST(incarceration AS INT64) + CAST(period_products AS INT64) +
             CAST(stis AS INT64)) as policy_area_count,
             
            CASE 
              WHEN abortion = TRUE THEN 'Abortion'
              WHEN contraception = TRUE THEN 'Contraception'
              WHEN minors = TRUE THEN 'Minors'
              WHEN sex_education = TRUE THEN 'Sex Education'
              WHEN insurance = TRUE THEN 'Insurance'
              WHEN pregnancy = TRUE THEN 'Pregnancy'
              WHEN refusal = TRUE THEN 'Refusal'
              WHEN appropriations = TRUE THEN 'Appropriations'
              WHEN emergency_contraception = TRUE THEN 'Emergency Contraception'
              WHEN fetal_issues = TRUE THEN 'Fetal Issues'
              WHEN fetal_tissue = TRUE THEN 'Fetal Tissue'
              WHEN incarceration = TRUE THEN 'Incarceration'
              WHEN period_products = TRUE THEN 'Period Products'
              WHEN stis = TRUE THEN 'STIs'
              ELSE 'Other/Multiple'
            END as primary_policy_area,
            
            topic_1, topic_2, topic_3, topic_4, topic_5, topic_6, topic_7, topic_8, topic_9, topic_10,
            COALESCE(topic_1, topic_2, topic_3, topic_4, topic_5, topic_6, topic_7, topic_8, topic_9, topic_10, 'No Topic') as primary_topic,
            
            (CASE WHEN topic_1 IS NOT NULL AND topic_1 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_2 IS NOT NULL AND topic_2 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_3 IS NOT NULL AND topic_3 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_4 IS NOT NULL AND topic_4 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_5 IS NOT NULL AND topic_5 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_6 IS NOT NULL AND topic_6 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_7 IS NOT NULL AND topic_7 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_8 IS NOT NULL AND topic_8 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_9 IS NOT NULL AND topic_9 != '' THEN 1 ELSE 0 END +
             CASE WHEN topic_10 IS NOT NULL AND topic_10 != '' THEN 1 ELSE 0 END) as topic_count,
            
            migration_date, data_source,
            
            CASE WHEN enacted = TRUE THEN TRUE ELSE FALSE END as is_successful,
            CASE WHEN (dead = TRUE OR vetoed = TRUE) THEN TRUE ELSE FALSE END as is_failed,
            CASE WHEN data_year >= 2020 THEN TRUE ELSE FALSE END as is_recent

          FROM `{self.project_id}.{self.dataset_id}.all_historical_bills_unified`
          WHERE state IS NOT NULL AND bill_number IS NOT NULL
        )
        SELECT 
          *,
          CASE 
            WHEN policy_area_count >= 4 THEN 'Complex (4+ areas)'
            WHEN policy_area_count = 3 THEN 'Medium (3 areas)'
            WHEN policy_area_count = 2 THEN 'Simple (2 areas)'
            WHEN policy_area_count = 1 THEN 'Single Focus'
            ELSE 'No Focus Areas'
          END as policy_complexity,
          
          CASE WHEN (policy_area_count >= 3 AND topic_count >= 2) THEN TRUE ELSE FALSE END as is_high_activity_bill
          
        FROM enhanced_bills
        """
        
        try:
            job = self.bq_client.query(create_table_sql)
            job.result(timeout=600)
            self.logger.info("✅ Created authentic comprehensive view: comprehensive_bills_authentic")
            self.logger.info("    🔍 Preserves NULL patterns showing data evolution")
            return True
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("❌ Failed to create Looker table: %s", e)
            return False

    def create_raw_data_tracking_view(self):
        """Create view showing what fields were actually tracked each year."""
        self.logger.info("🔄 Creating raw data tracking view...")
        
        tracking_view_sql = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.raw_data_tracking_by_year` AS
        SELECT 
          data_year,
          COUNT(*) as total_bills,
          
          -- Basic data collection (should always be tracked)
          SUM(CASE WHEN state IS NOT NULL THEN 1 ELSE 0 END) as has_state_data,
          SUM(CASE WHEN bill_number IS NOT NULL THEN 1 ELSE 0 END) as has_bill_number_data,
          SUM(CASE WHEN description IS NOT NULL THEN 1 ELSE 0 END) as has_description_data,
          SUM(CASE WHEN history IS NOT NULL THEN 1 ELSE 0 END) as has_history_data,
          
          -- Bill classification evolution
          SUM(CASE WHEN bill_type IS NOT NULL THEN 1 ELSE 0 END) as has_bill_type_data,
          SUM(CASE WHEN internal_summary IS NOT NULL THEN 1 ELSE 0 END) as has_internal_summary_data,
          SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) as has_notes_data,
          SUM(CASE WHEN website_blurb IS NOT NULL THEN 1 ELSE 0 END) as has_website_blurb_data,
          
          -- Date tracking evolution  
          SUM(CASE WHEN introduced_date IS NOT NULL THEN 1 ELSE 0 END) as has_introduced_date_data,
          SUM(CASE WHEN last_action_date IS NOT NULL THEN 1 ELSE 0 END) as has_last_action_date_data,
          SUM(CASE WHEN effective_date IS NOT NULL THEN 1 ELSE 0 END) as has_effective_date_data,
          SUM(CASE WHEN enacted_date IS NOT NULL THEN 1 ELSE 0 END) as has_enacted_date_data,
          
          -- Policy category tracking (NULL = not tracked, TRUE/FALSE = tracked)
          COUNTIF(abortion IS NOT NULL) as tracked_abortion_bills,
          COUNTIF(abortion = TRUE) as marked_abortion_true,
          COUNTIF(contraception IS NOT NULL) as tracked_contraception_bills,
          COUNTIF(contraception = TRUE) as marked_contraception_true,
          COUNTIF(minors IS NOT NULL) as tracked_minors_bills,
          COUNTIF(minors = TRUE) as marked_minors_true,
          COUNTIF(sex_education IS NOT NULL) as tracked_sex_education_bills,
          COUNTIF(sex_education = TRUE) as marked_sex_education_true,
          COUNTIF(insurance IS NOT NULL) as tracked_insurance_bills,
          COUNTIF(insurance = TRUE) as marked_insurance_true,
          COUNTIF(pregnancy IS NOT NULL) as tracked_pregnancy_bills,
          COUNTIF(pregnancy = TRUE) as marked_pregnancy_true,
          COUNTIF(emergency_contraception IS NOT NULL) as tracked_emergency_contraception_bills,
          COUNTIF(emergency_contraception = TRUE) as marked_emergency_contraception_true,
          COUNTIF(period_products IS NOT NULL) as tracked_period_products_bills,
          COUNTIF(period_products = TRUE) as marked_period_products_true,
          COUNTIF(incarceration IS NOT NULL) as tracked_incarceration_bills,
          COUNTIF(incarceration = TRUE) as marked_incarceration_true,
          
          -- Status field tracking (modern methodology post-2006)
          COUNTIF(introduced IS NOT NULL) as tracked_introduced_status,
          COUNTIF(introduced = TRUE) as marked_introduced_true,
          COUNTIF(enacted IS NOT NULL) as tracked_enacted_status,
          COUNTIF(enacted = TRUE) as marked_enacted_true,
          COUNTIF(vetoed IS NOT NULL) as tracked_vetoed_status,
          COUNTIF(vetoed = TRUE) as marked_vetoed_true,
          COUNTIF(dead IS NOT NULL) as tracked_dead_status,
          COUNTIF(dead = TRUE) as marked_dead_true,
          COUNTIF(pending IS NOT NULL) as tracked_pending_status,
          COUNTIF(pending = TRUE) as marked_pending_true,
          
          -- Intent classification tracking
          COUNTIF(positive IS NOT NULL) as tracked_positive_intent,
          COUNTIF(positive = TRUE) as marked_positive_true,
          COUNTIF(neutral IS NOT NULL) as tracked_neutral_intent,
          COUNTIF(neutral = TRUE) as marked_neutral_true,
          COUNTIF(restrictive IS NOT NULL) as tracked_restrictive_intent,
          COUNTIF(restrictive = TRUE) as marked_restrictive_true,
          
          -- Calculate tracking percentages for key fields
          ROUND(SUM(CASE WHEN bill_type IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as bill_type_tracking_pct,
          ROUND(SUM(CASE WHEN introduced_date IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as introduced_date_tracking_pct,
          ROUND(COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100, 1) as abortion_tracking_pct,
          ROUND(COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100, 1) as contraception_tracking_pct,
          ROUND(COUNTIF(positive IS NOT NULL) / COUNT(*) * 100, 1) as intent_tracking_pct,
          
          -- Calculate marking percentages (when tracked, what % was marked TRUE)
          CASE 
            WHEN COUNTIF(abortion IS NOT NULL) > 0 
            THEN ROUND(COUNTIF(abortion = TRUE) / COUNTIF(abortion IS NOT NULL) * 100, 1)
            ELSE NULL 
          END as abortion_true_rate_when_tracked,
          
          CASE 
            WHEN COUNTIF(contraception IS NOT NULL) > 0 
            THEN ROUND(COUNTIF(contraception = TRUE) / COUNTIF(contraception IS NOT NULL) * 100, 1)
            ELSE NULL 
          END as contraception_true_rate_when_tracked,
          
          CASE 
            WHEN COUNTIF(introduced IS NOT NULL) > 0 
            THEN ROUND(COUNTIF(introduced = TRUE) / COUNTIF(introduced IS NOT NULL) * 100, 1)
            ELSE NULL 
          END as introduced_true_rate_when_tracked,
          
          CASE 
            WHEN COUNTIF(enacted IS NOT NULL) > 0 
            THEN ROUND(COUNTIF(enacted = TRUE) / COUNTIF(enacted IS NOT NULL) * 100, 1)
            ELSE NULL 
          END as enacted_true_rate_when_tracked

        FROM `{self.project_id}.{self.dataset_id}.all_historical_bills_unified`
        GROUP BY data_year
        ORDER BY data_year
        """
        
        try:
            job = self.bq_client.query(tracking_view_sql)
            job.result(timeout=300)
            self.logger.info("✅ Created raw data tracking view: raw_data_tracking_by_year")
            return True
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("❌ Failed to create raw data tracking view: %s", e)
            return False

    def create_analytics_views(self):
        """Create comprehensive analytics views for state/year analysis."""
        self.logger.info("🔄 Creating analytics views...")
        
        analytics_sql_path = self.base_path / "sql" / "state_year_analytics.sql"
        
        if not analytics_sql_path.exists():
            self.logger.warning("Analytics SQL file not found: %s", analytics_sql_path)
            return False
            
        # Read and execute analytics SQL
        with open(analytics_sql_path) as f:
            analytics_sql = f.read()
            
        # Replace placeholders
        analytics_sql = analytics_sql.replace("{{ project_id }}", self.project_id)
        analytics_sql = analytics_sql.replace("{{ dataset_id }}", self.dataset_id)
        
        # Execute each statement separately
        statements = [stmt.strip() for stmt in analytics_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            try:
                self.logger.info("Executing analytics statement %d/%d", i+1, len(statements))
                job = self.bq_client.query(statement)
                job.result(timeout=300)
                self.logger.info("✓ Analytics statement %d completed", i+1)
            except Exception as e:
                self.logger.error("✗ Analytics statement %d failed: %s", i+1, e)
                return False
                
        self.logger.info("✅ Created all analytics views successfully")
        return True

    def run_migration(self) -> bool:
        """Run the complete migration."""
        self.logger.info("🚀 Starting Guttmacher historical data migration...")
        
        if not self.validate_setup():
            return False
        
        # Process database files
        db_files = sorted(list(self.data_path.glob("*.mdb")) + list(self.data_path.glob("*.accdb")))
        self.logger.info("📋 Found %d database files to migrate", len(db_files))
        
        for db_file in db_files:
            try:
                self.process_db_file(db_file)
            except Exception as e:
                error_msg = f"Critical error processing {db_file.name}: {e}"
                self.logger.error(error_msg)
                self.stats["errors"].append(error_msg)
        
        # Create views and tables if successful
        if self.stats["files_processed"] > 0:
            self.create_unified_view()
            self.create_looker_table()
            self.create_raw_data_tracking_view()
            self.create_analytics_views()
            self.generate_final_report()
            return True
        else:
            self.logger.error("❌ No files were successfully processed")
            return False

    def test_migration(self) -> bool:
        """Test migration results."""
        print("🧪 TESTING MIGRATION RESULTS")
        print("=" * 50)
        
        try:
            # Test main table
            table_ref = f"{self.project_id}.{self.dataset_id}.looker_comprehensive_bills"
            
            # Basic stats
            stats_query = f"""
            SELECT 
              COUNT(*) as total_rows,
              COUNT(DISTINCT state_code) as unique_states,
              COUNT(DISTINCT data_year) as unique_years,
              MIN(data_year) as earliest_year,
              MAX(data_year) as latest_year,
              SUM(CAST(is_successful AS INT64)) as total_enacted
            FROM `{table_ref}`
            """
            
            result = self.bq_client.query(stats_query).result()
            stats = next(result)
            
            print(f"✅ Total Bills: {stats.total_rows:,}")
            print(f"✅ States: {stats.unique_states}")
            print(f"✅ Years: {stats.earliest_year}-{stats.latest_year} ({stats.unique_years} years)")
            print(f"✅ Enacted Bills: {stats.total_enacted:,}")
            
            # Data quality
            quality_query = f"""
            SELECT 
              SUM(CASE WHEN state_code IS NULL THEN 1 ELSE 0 END) as missing_state,
              SUM(CASE WHEN bill_number IS NULL THEN 1 ELSE 0 END) as missing_bill_number,
              SUM(CASE WHEN intent = 'Unclassified' THEN 1 ELSE 0 END) as unclassified_intent
            FROM `{table_ref}`
            """
            
            quality_result = self.bq_client.query(quality_query).result()
            quality = next(quality_result)
            
            print(f"✅ Data Quality: {quality.missing_state} missing states, {quality.missing_bill_number} missing bill numbers")
            print(f"✅ Intent Classification: {quality.unclassified_intent:,} unclassified bills")
            
            print("\n🎉 Migration test PASSED!")
            return True
            
        except Exception as e:
            print(f"❌ Migration test FAILED: {e}")
            return False

    def cleanup_old_objects(self) -> bool:
        """Clean up old migration objects."""
        print("🧹 Cleaning up old objects...")
        
        try:
            query = f"""
            SELECT table_name, table_type
            FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`
            ORDER BY table_name
            """
            
            results = self.bq_client.query(query).result()
            objects = [(row.table_name, row.table_type) for row in results]
            
            # Objects to keep
            keep_objects = {"looker_comprehensive_bills", "all_historical_bills_unified"}
            for year in range(2002, 2025):
                keep_objects.add(f"historical_bills_{year}")
            
            # Remove old objects
            removed = 0
            for obj_name, obj_type in objects:
                if obj_name not in keep_objects:
                    try:
                        table_ref = f"{self.project_id}.{self.dataset_id}.{obj_name}"
                        self.bq_client.delete_table(table_ref)
                        print(f"✅ Removed {obj_name}")
                        removed += 1
                    except Exception as e:
                        print(f"⚠️  Failed to remove {obj_name}: {e}")
            
            print(f"🧹 Cleanup complete: {removed} objects removed")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False

    def generate_final_report(self):
        """Generate migration completion report."""
        duration = datetime.now() - self.stats["start_time"]
        
        print("\n" + "="*80)
        print("🎉 GUTTMACHER MIGRATION COMPLETE!")
        print("="*80)
        print(f"⏱️  Total Time: {duration.total_seconds():.1f} seconds")
        print(f"📁 Files Processed: {self.stats['files_processed']}")
        print(f"📅 Years: {sorted(self.stats['years_processed'])}")
        print(f"📋 Total Bills: {self.stats['total_bills']:,}")
        print(f"📊 Field Mappings Applied: {self.stats['field_mappings_applied']}")
        
        if self.stats["errors"]:
            print(f"\n⚠️  Errors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:3]:
                print(f"   • {error}")
        
        print(f"\n🎯 BigQuery Dataset: {self.project_id}.{self.dataset_id}")
        print("📊 Main Looker Table: looker_comprehensive_bills")
        print("\n🔧 Looker Studio Connection:")
        print(f"  Project: {self.project_id}")
        print(f"  Dataset: {self.dataset_id}")
        print("  Table: looker_comprehensive_bills")
        print("="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Guttmacher Legislative Tracker Migration")
    parser.add_argument("--test", action="store_true", help="Test migration results")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old objects")
    parser.add_argument("--looker-only", action="store_true", help="Create just Looker table")
    
    args = parser.parse_args()
    
    try:
        migration = GuttmacherMigration()
        
        if args.test:
            success = migration.test_migration()
        elif args.cleanup:
            success = migration.cleanup_old_objects()
        elif args.looker_only:
            success = migration.create_looker_table()
        else:
            success = migration.run_migration()
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()