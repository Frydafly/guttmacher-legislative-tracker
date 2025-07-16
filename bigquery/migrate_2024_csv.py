#!/usr/bin/env python3
"""
GUTTMACHER LEGISLATIVE TRACKER - 2024 CSV DATA MIGRATION
========================================================

Specialized script to migrate 2024 legislative data from CSV format.
Uses the same field mappings and schema harmonization as the main migration.

Usage:
    python migrate_2024_csv.py data/2024_bills.csv
"""

import argparse
import logging
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import yaml
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud import exceptions as google_exceptions


class CSV2024Migration:
    """Migrate 2024 CSV data to BigQuery."""

    def __init__(self):
        """Initialize the migration."""
        load_dotenv()

        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv(
            "BQ_DATASET_ID", "legislative_tracker_historical"
        )

        if not self.project_id or self.project_id == "your-actual-project-id":
            raise ValueError("Please set GCP_PROJECT_ID in .env file")

        self.bq_client = bigquery.Client(project=self.project_id)
        self.base_path = Path(__file__).parent

        # Load field mappings
        self.field_mappings = self._load_field_mappings()

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.base_path / "logs" / "csv_migration_2024.log", mode="a")
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_field_mappings(self) -> Dict[str, Any]:
        """Load field mappings configuration."""
        mappings_path = self.base_path / "field_mappings.yaml"
        if not mappings_path.exists():
            raise FileNotFoundError(f"Field mappings file not found: {mappings_path}")

        with open(mappings_path, 'r', encoding='utf-8') as f:
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
                            reverse_map[variant.lower()] = standard_name
                            reverse_map[variant] = standard_name
        return reverse_map

    def read_csv(self, csv_path: Path) -> pd.DataFrame:
        """Read CSV file with proper encoding and type handling."""
        self.logger.info(f"📄 Reading CSV file: {csv_path}")

        try:
            # Try UTF-8 first
            df = pd.read_csv(csv_path, low_memory=False)
        except UnicodeDecodeError:
            # Fall back to Latin-1 if UTF-8 fails
            self.logger.warning("UTF-8 decoding failed, trying Latin-1")
            df = pd.read_csv(csv_path, encoding='latin-1', low_memory=False)

        self.logger.info(f"✅ Read {len(df)} rows from CSV")
        self.logger.info(f"📊 Columns found: {list(df.columns)}")

        return df

    def harmonize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Harmonize DataFrame schema to match BigQuery expectations."""
        if df.empty:
            return df

        self.logger.info("🔧 Harmonizing schema...")

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
        status_fields = {
            'introduced', 'seriously_considered', 'passed_first_chamber',
            'passed_second_chamber', 'enacted', 'vetoed', 'dead', 'pending'
        }

        for field in all_standard_fields:
            field_type = self.field_mappings.get('bigquery_types', {}).get(field, 'STRING')
            if field_type == 'BOOLEAN':
                if field in status_fields:
                    standardized_data[field] = False
                else:
                    standardized_data[field] = None
            else:
                standardized_data[field] = None

        # Map existing columns (case-insensitive matching)
        mapped_count = 0
        unmapped_columns = []

        for original_col in df.columns:
            mapped = False
            # Try exact match first
            if original_col in reverse_map:
                standard_name = reverse_map[original_col]
                standardized_data[standard_name] = df[original_col]
                mapped_count += 1
                mapped = True
            # Try lowercase match
            elif original_col.lower() in reverse_map:
                standard_name = reverse_map[original_col.lower()]
                standardized_data[standard_name] = df[original_col]
                mapped_count += 1
                mapped = True
            # Try removing spaces and special characters
            else:
                cleaned_col = original_col.replace(' ', '').replace('_', '').lower()
                for variant, standard in reverse_map.items():
                    if variant.replace(' ', '').replace('_', '').lower() == cleaned_col:
                        standardized_data[standard] = df[original_col]
                        mapped_count += 1
                        mapped = True
                        break

            if not mapped:
                unmapped_columns.append(original_col)

        self.logger.info(f"✅ Mapped {mapped_count} columns")
        if unmapped_columns:
            self.logger.warning(f"⚠️  Unmapped columns: {unmapped_columns}")

        # Add metadata
        standardized_data['data_year'] = 2024
        standardized_data['migration_date'] = date.today()
        standardized_data['data_source'] = "CSV Import 2024"

        # Create DataFrame with consistent length
        if len(df) > 0:
            for key, value in standardized_data.items():
                if not isinstance(value, pd.Series):
                    standardized_data[key] = [value] * len(df)

        # Create DataFrame and add missing columns for schema compatibility
        result_df = pd.DataFrame(standardized_data)

        # Add the invalid columns that exist in other tables for schema compatibility
        # These columns shouldn't exist but are in the historical data
        compatibility_columns = ['2005', '2006_2007', '2008_2014', '2015_2018', '2019_2024']
        for col in compatibility_columns:
            if col not in result_df.columns:
                result_df[col] = None

        return result_df

    def clean_dataframe_for_bigquery(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for BigQuery compatibility."""
        if df.empty:
            return df

        self.logger.info("🧹 Cleaning data for BigQuery...")
        df_clean = df.copy()

        # Handle date fields
        date_fields = ['last_action_date', 'introduced_date', 'enacted_date', 'vetoed_date']
        for col in date_fields:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

        datetime_fields = ['date_last_updated']
        for col in datetime_fields:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

        # Clean string fields
        string_fields = ['state', 'bill_type', 'bill_number', 'description', 'history', 'notes',
                        'website_blurb', 'internal_summary', 'data_source', 'effective_date']

        # Add all topic fields to string fields
        topic_fields = [f'topic_{i}' for i in range(1, 11)]
        string_fields.extend(topic_fields)

        for col in string_fields:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(['nan', 'None', ''], None)

        # Handle boolean fields
        boolean_fields = [k for k, v in self.field_mappings.get('bigquery_types', {}).items()
                         if v == 'BOOLEAN']
        for col in boolean_fields:
            if col in df_clean.columns:
                # Convert various representations to boolean
                df_clean[col] = df_clean[col].fillna(False)
                df_clean[col] = df_clean[col].astype(str).str.lower()
                df_clean[col] = df_clean[col].map({
                    'true': True, '1': True, 'yes': True, 'y': True,
                    'false': False, '0': False, 'no': False, 'n': False,
                    'nan': False, '': False, 'none': False
                })
                df_clean[col] = df_clean[col].fillna(False).astype(bool)

        # Handle integer fields
        integer_fields = [k for k, v in self.field_mappings.get('bigquery_types', {}).items()
                         if v == 'INTEGER']
        for col in integer_fields:
            if col in df_clean.columns:
                # Convert to numeric, replacing non-numeric with NaN
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                # For ID field, we can't have NaN, so fill with 0
                if col == 'id':
                    df_clean[col] = df_clean[col].fillna(0).astype(int)
                else:
                    # For other integer fields, convert to nullable integer
                    df_clean[col] = df_clean[col].astype('Int64')

        return df_clean

    def load_to_bigquery(self, df: pd.DataFrame) -> bool:
        """Load DataFrame to BigQuery."""
        if df.empty:
            self.logger.error("❌ No data to load")
            return False

        table_name = "historical_bills_2024"
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        self.logger.info(f"📤 Loading data to {table_name}...")

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
            # Debug: Check data types
            self.logger.debug("DataFrame dtypes:")
            for col, dtype in df.dtypes.items():
                self.logger.debug(f"  {col}: {dtype}")

            # Check for problematic integer columns
            for col in df.columns:
                if df[col].dtype.name in ['int64', 'Int64']:
                    if df[col].isna().any():
                        self.logger.warning(f"Column {col} has NaN values but is type {df[col].dtype}")

            job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result(timeout=300)
            self.logger.info(f"✅ Successfully loaded {len(df)} rows to {table_name}")
            return True
        except google_exceptions.GoogleCloudError as e:
            self.logger.error(f"❌ Failed to load to BigQuery: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed with error: {type(e).__name__}: {e}")
            # Try to identify problematic columns
            for col in df.columns:
                try:
                    if df[col].dtype == 'object':
                        # Try to convert to see if it fails
                        _ = df[col].astype(str)
                except Exception as col_e:
                    self.logger.error(f"  Problem with column {col}: {col_e}")
            return False

    def update_unified_views(self):
        """Update the unified views to include 2024 data."""
        self.logger.info("🔄 Updating unified views...")

        # Check if the materialized table exists
        try:
            self.bq_client.get_table(f"{self.project_id}.{self.dataset_id}.all_historical_bills_materialized")

            # Recreate the materialized table to include 2024
            recreate_sql = f"""
            CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.all_historical_bills_materialized`
            AS
            SELECT * FROM `{self.project_id}.{self.dataset_id}.all_historical_bills_unified`
            """

            job = self.bq_client.query(recreate_sql)
            job.result(timeout=600)
            self.logger.info("✅ Updated materialized table with 2024 data")

        except google_exceptions.NotFound:
            self.logger.warning("⚠️  Materialized table not found, skipping update")
        except Exception as e:
            self.logger.error(f"❌ Failed to update views: {e}")

    def migrate_csv(self, csv_path: Path) -> bool:
        """Run the CSV migration."""
        self.logger.info(f"🚀 Starting 2024 CSV migration")

        try:
            # Read CSV
            df = self.read_csv(csv_path)

            # Harmonize schema
            df_harmonized = self.harmonize_schema(df)

            # Clean for BigQuery
            df_clean = self.clean_dataframe_for_bigquery(df_harmonized)

            # Load to BigQuery
            if self.load_to_bigquery(df_clean):
                # Update unified views
                self.update_unified_views()

                self.logger.info("🎉 Migration completed successfully!")
                self.logger.info(f"📊 Migrated {len(df)} bills from 2024")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"❌ Migration failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate 2024 legislative data from CSV to BigQuery"
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Path to the 2024 CSV file"
    )

    args = parser.parse_args()
    csv_path = Path(args.csv_file)

    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    try:
        migration = CSV2024Migration()
        success = migration.migrate_csv(csv_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
