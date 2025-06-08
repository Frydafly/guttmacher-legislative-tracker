#!/usr/bin/env python3
"""
ONE-TIME HISTORICAL DATA MIGRATION PIPELINE
===========================================

Single script to migrate all historical .mdb files (2002-2024) to BigQuery.
This consolidates all functionality into one simple script for the migration.

Usage:
    python migration_pipeline.py

Prerequisites:
    1. brew install mdbtools
    2. pip install -r requirements.txt
    3. gcloud auth application-default login
    4. Copy .mdb files to ./data/
    5. Configure .env file with GCP_PROJECT_ID
"""

import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud import exceptions as google_exceptions
from tqdm import tqdm


class MigrationPipeline:
    """Complete historical data migration for one-time use."""

    def __init__(self):
        """Initialize the migration pipeline."""
        # Load environment
        load_dotenv()

        # Configuration
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = "legislative_tracker_historical"

        if not self.project_id or self.project_id == "your-actual-project-id":
            raise ValueError("Please set GCP_PROJECT_ID in .env file")

        # Setup BigQuery client
        self.bq_client = bigquery.Client(project=self.project_id)

        # Setup paths
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"

        # Migration statistics
        self.stats = {
            "start_time": datetime.now(),
            "files_processed": 0,
            "total_bills": 0,
            "total_categories": 0,
            "years_processed": [],
            "errors": []
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

    def validate_setup(self) -> bool:
        """Validate that everything is ready for migration."""
        self.logger.info("🔍 Validating migration setup...")

        # Check mdbtools
        try:
            result = subprocess.run(
                ["mdb-tables", "--help"],
                capture_output=True, text=True, check=False
            )
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

        # Check for MDB files
        mdb_files = list(self.data_path.glob("*.mdb"))
        if not mdb_files:
            self.logger.error("❌ No .mdb files found in %s", self.data_path)
            self.logger.error("   Please copy your .mdb files to this directory")
            return False

        self.logger.info("✅ Found %d .mdb files for migration", len(mdb_files))
        return True

    def extract_year_from_filename(self, mdb_path: Path) -> Optional[int]:
        """Extract year from MDB filename."""
        year_match = re.search(r"(\d{4})", mdb_path.name)
        if not year_match:
            self.logger.warning("⚠️  Could not extract year from %s", mdb_path.name)
            return None
        return int(year_match[1])

    def get_tables_from_mdb(self, mdb_path: Path) -> List[str]:
        """Get list of tables from MDB file."""
        try:
            result = subprocess.run(
                ["mdb-tables", "-1", str(mdb_path)],
                capture_output=True, text=True, timeout=30, check=False
            )
            if result.returncode != 0:
                self.logger.error("Failed to list tables: %s", result.stderr)
                return []

            return [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout listing tables in %s", mdb_path.name)
            return []

    def export_table_to_dataframe(self, mdb_path: Path, table: str) -> Optional[pd.DataFrame]:
        """Export a single table directly to DataFrame."""
        try:
            result = subprocess.run(
                ["mdb-export", str(mdb_path), table],
                capture_output=True, text=True, timeout=120, check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                # Use StringIO to read CSV data directly into pandas
                from io import StringIO
                df = pd.read_csv(StringIO(result.stdout), low_memory=False)
                return None if df.empty else df
            return None

        except (subprocess.TimeoutExpired, OSError, pd.errors.ParserError) as e:
            self.logger.warning("Failed to export %s: %s", table, e)
            return None

    def clean_dataframe_for_bigquery(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """Clean DataFrame for BigQuery compatibility."""
        df_clean = df.copy()

        # Add migration metadata
        df_clean["data_year"] = year
        df_clean["migration_date"] = datetime.now().date()
        df_clean["data_source"] = "Historical Migration"

        # Clean column names for BigQuery
        df_clean.columns = [
            re.sub(r"[^a-zA-Z0-9_]", "_", str(col)).strip("_").lower()
            for col in df_clean.columns
        ]

        # Remove empty rows/columns
        df_clean = df_clean.dropna(axis=1, how="all")  # Empty columns
        df_clean = df_clean.dropna(axis=0, how="all")  # Empty rows

        # Convert dates
        for col in df_clean.columns:
            if "date" in col and df_clean[col].dtype == "object":
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")

        # Clean strings
        for col in df_clean.columns:
            if df_clean[col].dtype == "object":
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(["nan", "None", ""], None)

        return df_clean

    def load_to_bigquery(self, df: pd.DataFrame, table_name: str) -> bool:
        """Load DataFrame to BigQuery."""
        if df.empty:
            self.logger.warning("Empty DataFrame for %s", table_name)
            return False

        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True,
            create_disposition="CREATE_IF_NEEDED"
        )

        try:
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result(timeout=300)

            self.logger.info("✅ Loaded %d rows to %s", len(df), table_name)
            return True

        except google_exceptions.GoogleCloudError as e:
            self.logger.error("❌ Failed to load %s: %s", table_name, e)
            return False

    def process_mdb_file(self, mdb_path: Path) -> bool:
        """Process a single MDB file."""
        year = self.extract_year_from_filename(mdb_path)
        if not year:
            return False

        self.logger.info("📁 Processing %s (%d)", mdb_path.name, year)

        # Get tables
        tables = self.get_tables_from_mdb(mdb_path)
        if not tables:
            self.logger.error("No tables found in %s", mdb_path.name)
            return False

        self.logger.info("Found %d tables: %s", len(tables), ", ".join(tables))

        success_count = 0
        bills_count = 0
        categories_count = 0

        # Process each table
        for table in tqdm(tables, desc=f"Processing {year}"):
            df = self.export_table_to_dataframe(mdb_path, table)
            if df is None or df.empty:
                continue

            try:
                # Clean for BigQuery
                df_clean = self.clean_dataframe_for_bigquery(df, year)

                # Determine table type and name
                table_lower = table.lower()
                if any(kw in table_lower for kw in ["legislative", "bill", "law"]):
                    table_type = "bills"
                    bills_count += len(df_clean)
                elif any(kw in table_lower for kw in ["issue", "category", "policy"]):
                    table_type = "categories"
                    categories_count += len(df_clean)
                else:
                    table_type = "other"

                table_name = f"historical_{table_type}_{year}"

                # Load to BigQuery
                if self.load_to_bigquery(df_clean, table_name):
                    success_count += 1

            except (pd.errors.ParserError, OSError, ValueError) as e:
                self.logger.error("Error processing table %s: %s", table, e)
                continue

        # Update statistics
        if success_count > 0:
            self.stats["files_processed"] += 1
            self.stats["years_processed"].append(year)
            self.stats["total_bills"] += bills_count
            self.stats["total_categories"] += categories_count
            self.logger.info(
                "✅ Processed %d/%d tables from %d",
                success_count, len(tables), year
            )
            return True
        self.logger.error("❌ Failed to process any tables from %d", year)
        return False

    def create_union_views(self):
        """Create union views for analysis with schema harmonization."""
        self.logger.info("🔗 Creating union views with schema harmonization...")

        # Find all tables
        query = f"""
        SELECT table_name
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`
        WHERE table_name LIKE 'historical_%'
        ORDER BY table_name
        """

        try:
            results = self.bq_client.query(query).result()
            all_tables = [row.table_name for row in results]
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to list tables: %s", e)
            return

        # Group by type
        bills_tables = [t for t in all_tables if "_bills_" in t]
        categories_tables = [t for t in all_tables if "_categories_" in t]

        # Create union views with schema harmonization
        for table_group, view_name in [
            (bills_tables, "all_historical_bills"),
            (categories_tables, "all_historical_categories")
        ]:
            if not table_group:
                continue

            self._create_harmonized_union_view(table_group, view_name)

    def _create_harmonized_union_view(self, tables, view_name):
        """Create a union view with harmonized schema across all tables."""
        if not tables:
            return

        # Get all unique columns across all tables
        all_columns = set()
        table_schemas = {}

        for table in tables:
            schema_query = f"""
            SELECT column_name, data_type
            FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
            """
            
            try:
                schema_results = self.bq_client.query(schema_query).result()
                table_columns = {}
                for row in schema_results:
                    all_columns.add(row.column_name)
                    table_columns[row.column_name] = row.data_type
                table_schemas[table] = table_columns
            except google_exceptions.GoogleCloudError as e:
                self.logger.error("Failed to get schema for %s: %s", table, e)
                continue

        if not all_columns:
            self.logger.error("No columns found for union view %s", view_name)
            return

        # Sort columns for consistent ordering
        sorted_columns = sorted(all_columns)

        # Build harmonized SELECT statements for each table
        union_queries = []
        for table in tables:
            table_cols = table_schemas.get(table, {})
            select_parts = []

            for col in sorted_columns:
                if col in table_cols:
                    # Cast all columns to STRING to ensure compatibility
                    select_parts.append(f"CAST(`{col}` AS STRING) AS `{col}`")
                else:
                    # Add NULL as STRING for missing columns
                    select_parts.append(f"CAST(NULL AS STRING) AS `{col}`")

            select_statement = f"""
            SELECT {', '.join(select_parts)}
            FROM `{self.project_id}.{self.dataset_id}.{table}`
            """
            union_queries.append(select_statement)

        # Create the union view
        create_view = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.{view_name}` AS
        {' UNION ALL '.join(union_queries)}
        """

        try:
            job = self.bq_client.query(create_view)
            job.result()
            self.logger.info(
                "✅ Created harmonized view: %s (%d columns, %d tables)",
                view_name, len(sorted_columns), len(tables)
            )
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to create view %s: %s", view_name, e)

    def verify_bigquery_data(self):
        """Verify data was actually loaded to BigQuery."""
        verification_results = {}

        # Check bills data
        bills_query = f"""
        SELECT COUNT(*) as total_bills, COUNT(DISTINCT data_year) as years_count
        FROM `{self.project_id}.{self.dataset_id}.all_historical_bills`
        """

        try:
            result = self.bq_client.query(bills_query).result()
            row = next(result)
            verification_results["bills"] = {
                "total": row.total_bills,
                "years": row.years_count
            }
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to verify bills data: %s", e)
            verification_results["bills"] = {"error": str(e)}

        # Check categories data
        categories_query = f"""
        SELECT COUNT(*) as total_categories, COUNT(DISTINCT data_year) as years_count
        FROM `{self.project_id}.{self.dataset_id}.all_historical_categories`
        """

        try:
            result = self.bq_client.query(categories_query).result()
            row = next(result)
            verification_results["categories"] = {
                "total": row.total_categories,
                "years": row.years_count
            }
        except google_exceptions.GoogleCloudError as e:
            self.logger.error("Failed to verify categories data: %s", e)
            verification_results["categories"] = {"error": str(e)}

        return verification_results

    def generate_final_report(self):
        """Generate migration completion report with BigQuery verification."""
        duration = datetime.now() - self.stats["start_time"]

        # Verify data in BigQuery
        verification = self.verify_bigquery_data()

        print("\n" + "="*80)
        print("🎉 HISTORICAL DATA MIGRATION COMPLETE!")
        print("="*80)
        print(f"⏱️  Total Time: {duration.total_seconds():.1f} seconds")
        print(f"📁 Files Processed: {self.stats['files_processed']}")
        print(f"📅 Years: {sorted(self.stats['years_processed'])}")
        print(f"📋 Total Bills: {self.stats['total_bills']:,}")
        print(f"📂 Total Categories: {self.stats['total_categories']:,}")

        # BigQuery verification
        print("\n🔍 BIGQUERY VERIFICATION:")
        if "error" not in verification.get("bills", {}):
            bills_data = verification["bills"]
            print(f"✅ Bills in BigQuery: {bills_data['total']:,} rows across {bills_data['years']} years")
        else:
            print(f"❌ Bills verification failed: {verification['bills']['error']}")

        if "error" not in verification.get("categories", {}):
            cats_data = verification["categories"]
            print(f"✅ Categories in BigQuery: {cats_data['total']:,} rows across {cats_data['years']} years")
        else:
            print(f"❌ Categories verification failed: {verification['categories']['error']}")

        if self.stats["errors"]:
            print(f"\n⚠️  Errors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:5]:
                print(f"   • {error}")

        print(f"\n🎯 BigQuery Dataset: {self.project_id}.{self.dataset_id}")
        print("📊 Ready for Looker Studio connection!")
        print("🗂️  Main views: all_historical_bills, all_historical_categories")
        print("="*80)

    def run_migration(self) -> bool:
        """Run the complete migration."""
        self.logger.info("🚀 Starting historical data migration...")

        # Validate setup
        if not self.validate_setup():
            return False

        # Find all MDB files
        mdb_files = sorted(list(self.data_path.glob("*.mdb")))
        self.logger.info("📋 Found %d MDB files to migrate", len(mdb_files))

        # Process each file
        for mdb_file in mdb_files:
            try:
                self.process_mdb_file(mdb_file)
            except (OSError, ValueError, RuntimeError) as e:
                error_msg = f"Critical error processing {mdb_file.name}: {e}"
                self.logger.error(error_msg)
                self.stats["errors"].append(error_msg)

        # Create union views if we processed any data
        if self.stats["files_processed"] > 0:
            self.create_union_views()
            self.generate_final_report()
            return True
        else:
            self.logger.error("❌ No files were successfully processed")
            return False


def main():
    """Run the migration pipeline."""
    try:
        pipeline = MigrationPipeline()
        success = pipeline.run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(130)
    except (ValueError, OSError, RuntimeError) as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
