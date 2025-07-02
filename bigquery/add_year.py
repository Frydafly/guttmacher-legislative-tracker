#!/usr/bin/env python3
"""
GUTTMACHER LEGISLATIVE TRACKER - SINGLE YEAR DATA ADDITION
=========================================================

Pipeline for adding a single year's data to the existing BigQuery dataset.
Useful for adding new years (2025+) or updating existing years with new data.

Usage:
    python add_year.py 2025                    # Add 2025 data
    python add_year.py 2024 --update           # Update existing 2024 data
    python add_year.py 2025 --test             # Test before adding

Prerequisites:
    1. BigQuery dataset exists (created by main migration)
    2. Place new year's .mdb/.accdb file in ./data/
    3. Configure .env file with GCP_PROJECT_ID
    4. Ensure field_mappings.yaml is up to date

File naming expectations:
    - 2025: "2025 state legislation*.mdb" or "2025*.accdb"
    - Files should be in ./data/ directory
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from google.cloud import exceptions as google_exceptions

# Import the main migration class
from migrate import GuttmacherMigration


class YearlyDataPipeline(GuttmacherMigration):
    """Pipeline for adding single year's data to existing BigQuery dataset."""
    
    def __init__(self, target_year: int):
        """Initialize the yearly pipeline.
        
        Args:
            target_year: The year of data to add/update
        """
        super().__init__()
        self.target_year = target_year
        self.table_name = f"historical_bills_{target_year}"
        
        # Setup logging for single year processing
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'yearly_migration_{target_year}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def find_year_database(self) -> Optional[Path]:
        """Find the database file for the target year.
        
        Returns:
            Path to the database file, or None if not found
        """
        data_dir = Path('./data')
        if not data_dir.exists():
            self.logger.error(f"Data directory not found: {data_dir}")
            return None
            
        # Common patterns for year files
        patterns = [
            f"{self.target_year}*.mdb",
            f"{self.target_year}*.accdb",
            f"*{self.target_year}*.mdb",
            f"*{self.target_year}*.accdb",
        ]
        
        for pattern in patterns:
            matches = list(data_dir.glob(pattern))
            if matches:
                if len(matches) > 1:
                    self.logger.warning(f"Multiple files found for {self.target_year}: {matches}")
                    self.logger.info(f"Using first match: {matches[0]}")
                return matches[0]
                
        self.logger.error(f"No database file found for year {self.target_year}")
        self.logger.info(f"Expected patterns: {patterns}")
        self.logger.info(f"Available files: {list(data_dir.glob('*'))}")
        return None
        
    def check_table_exists(self) -> bool:
        """Check if the target year's table already exists in BigQuery.
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_name)
            self.bq_client.get_table(table_ref)
            return True
        except google_exceptions.NotFound:
            return False
            
    def process_year(self, update_existing: bool = False, test_mode: bool = False) -> bool:
        """Process a single year's data.
        
        Args:
            update_existing: If True, replace existing table data
            test_mode: If True, only test without uploading to BigQuery
            
        Returns:
            True if successful, False otherwise
        """
        # Find database file
        db_file = self.find_year_database()
        if not db_file:
            return False
            
        # Check if table exists
        table_exists = self.check_table_exists()
        if table_exists and not update_existing:
            self.logger.error(f"Table {self.table_name} already exists. Use --update to replace.")
            return False
            
        self.logger.info(f"Processing {self.target_year} data from: {db_file}")
        
        try:
            # Extract data from database
            self.logger.info(f"Extracting data from {db_file}")
            # First need to find the main table in the database
            tables = self.get_tables_from_db(db_file)
            if not tables:
                self.logger.error("No tables found in %s", db_file)
                return False
                
            table_name = self.find_primary_table(tables)
            if not table_name:
                self.logger.error("Could not find primary table in %s", db_file)
                return False
            
            raw_df = self.export_table_to_dataframe(db_file, table_name)
            
            if raw_df is None or raw_df.empty:
                self.logger.warning(f"No data extracted from {db_file}")
                return False
                
            self.logger.info(f"Extracted {len(raw_df)} records from {self.target_year}")
            
            # Standardize data
            self.logger.info("Standardizing data schema")
            standardized_df = self.harmonize_schema(raw_df, self.target_year)
            
            # Clean for BigQuery
            self.logger.info("Cleaning data for BigQuery")
            clean_df = self.clean_dataframe_for_bigquery(standardized_df)
            
            if test_mode:
                self.logger.info("TEST MODE - Data processing successful")
                self.logger.info(f"Would upload {len(clean_df)} records to {self.table_name}")
                self.logger.info(f"Sample columns: {list(clean_df.columns)[:10]}")
                return True
                
            # Upload to BigQuery
            self.logger.info(f"Uploading to BigQuery table: {self.table_name}")
            self.load_to_bigquery(clean_df, self.table_name)
            
            # Update unified views
            self.logger.info("Updating unified views")
            self.create_unified_view()
            self.create_looker_table()
            self.create_analytics_views()
            
            self.logger.info(f"Successfully processed {self.target_year} data")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {self.target_year}: {str(e)}")
            return False
            
    def validate_year_data(self) -> bool:
        """Validate the uploaded year data.
        
        Returns:
            True if validation passes, False otherwise
        """
        if not self.check_table_exists():
            self.logger.error(f"Table {self.table_name} does not exist")
            return False
            
        try:
            # Basic validation queries
            query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT id) as unique_bills,
                COUNT(DISTINCT state) as states_covered,
                MIN(data_year) as min_year,
                MAX(data_year) as max_year
            FROM `{self.project_id}.{self.dataset_id}.{self.table_name}`
            """
            
            result = self.bq_client.query(query).to_dataframe()
            
            self.logger.info(f"Validation results for {self.target_year}:")
            self.logger.info(f"  Total records: {result.iloc[0]['total_records']}")
            self.logger.info(f"  Unique bills: {result.iloc[0]['unique_bills']}")
            self.logger.info(f"  States covered: {result.iloc[0]['states_covered']}")
            self.logger.info(f"  Year range: {result.iloc[0]['min_year']} - {result.iloc[0]['max_year']}")
            
            # Check if year matches
            if result.iloc[0]['min_year'] != self.target_year or result.iloc[0]['max_year'] != self.target_year:
                self.logger.warning(f"Year mismatch detected in data")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return False


def main():
    """Main entry point for yearly data pipeline."""
    parser = argparse.ArgumentParser(description='Add single year data to BigQuery')
    parser.add_argument('year', type=int, help='Year to add (e.g., 2025)')
    parser.add_argument('--update', action='store_true', 
                       help='Update existing year data (replace table)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - process data but do not upload')
    parser.add_argument('--validate', action='store_true',
                       help='Validate uploaded data')
    
    args = parser.parse_args()
    
    # Validate year
    if args.year < 2000 or args.year > 2030:
        print(f"Error: Year {args.year} is outside expected range (2000-2030)")
        sys.exit(1)
        
    # Initialize pipeline
    pipeline = YearlyDataPipeline(args.year)
    
    if args.validate:
        # Just validate existing data
        success = pipeline.validate_year_data()
        sys.exit(0 if success else 1)
    
    # Process the year
    success = pipeline.process_year(
        update_existing=args.update,
        test_mode=args.test
    )
    
    if success and not args.test:
        # Validate the uploaded data
        validation_success = pipeline.validate_year_data()
        if not validation_success:
            print("Warning: Data validation failed")
            
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()