#!/usr/bin/env python3
"""
Simplified bills pipeline - loads core fields only for initial success.
"""

import subprocess
import pandas as pd
from pathlib import Path
import re
from datetime import datetime, date
from google.cloud import bigquery
import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class SimpleBillsPipeline:
    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
        
        self.data_path = Path(__file__).parent.parent / 'data' / 'historical'
        self.staging_path = Path(__file__).parent.parent / 'data' / 'staging'
        self.staging_path.mkdir(exist_ok=True)
    
    def extract_and_clean_bills(self, mdb_path):
        """Extract and clean core bill fields only."""
        # Extract year from filename
        year_match = re.search(r'(\d{4})', mdb_path.name)
        if not year_match:
            logger.error(f"Could not extract year from {mdb_path.name}")
            return None, None
        
        data_year = int(year_match.group(1))
        
        # Extract the bills table only
        csv_file = self.staging_path / f"{data_year}_bills_simple.csv"
        with open(csv_file, 'w') as f:
            result = subprocess.run(
                ['mdb-export', str(mdb_path), 'state legislative table'],
                stdout=f,
                text=True
            )
        
        if result.returncode != 0:
            logger.error(f"Failed to extract bills from {mdb_path.name}")
            return None, None
        
        # Load and clean
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} bills from {data_year}")
        
        # Keep only core fields (no complex dates or arrays)
        core_fields = {
            'ID': 'bill_id',
            'State': 'state', 
            'Bill Number': 'bill_number',
            'Status': 'current_bill_status',
            'Bill Summary': 'summary',
            'Sponsor': 'sponsor',
            'Action': 'last_action_text'
        }
        
        # Map and rename fields
        available_fields = {}
        for original, target in core_fields.items():
            if original in df.columns:
                available_fields[original] = target
        
        if available_fields:
            df_clean = df[list(available_fields.keys())].copy()
            df_clean = df_clean.rename(columns=available_fields)
        else:
            logger.warning(f"No core fields found in {data_year}")
            return None, None
        
        # Add metadata
        df_clean['data_year'] = data_year
        df_clean['data_source'] = 'Historical'
        df_clean['import_date'] = date.today()
        df_clean['last_updated'] = datetime.now()
        
        # Clean string fields
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).replace('nan', None)
        
        # Clean column names for BigQuery
        df_clean.columns = df_clean.columns.str.replace(' ', '_', regex=False)
        df_clean.columns = df_clean.columns.str.replace('/', '_', regex=False)
        df_clean.columns = df_clean.columns.str.replace('[^A-Za-z0-9_]', '_', regex=True)
        df_clean.columns = df_clean.columns.str.replace('__+', '_', regex=True)
        df_clean.columns = df_clean.columns.str.strip('_')
        df_clean.columns = df_clean.columns.str.lower()
        
        logger.info(f"Cleaned data shape: {df_clean.shape}")
        logger.info(f"Final columns: {list(df_clean.columns)}")
        
        return df_clean, data_year
    
    def load_to_bigquery(self, df, data_year):
        """Load simplified data to BigQuery."""
        table_name = f"simple_bills_{data_year}"
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True
        )
        
        try:
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()
            
            logger.info(f"✓ Loaded {len(df)} bills to {table_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Error loading to {table_id}: {e}")
            return False
    
    def create_union_table(self):
        """Create union table for all simple bills."""
        logger.info("Creating union table for simple bills")
        
        # Find all simple bills tables
        query = f"""
        SELECT table_name 
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES` 
        WHERE table_name LIKE 'simple_bills_%'
        ORDER BY table_name
        """
        
        tables = []
        try:
            results = self.bq_client.query(query).result()
            tables = [row.table_name for row in results]
        except Exception as e:
            logger.error(f"Error finding tables: {e}")
            return False
        
        if not tables:
            logger.error("No simple bills tables found")
            return False
        
        # Build UNION ALL query
        union_queries = []
        for table_name in tables:
            union_queries.append(f"""
                SELECT * FROM `{self.project_id}.{self.dataset_id}.{table_name}`
            """)
        
        union_query = " UNION ALL ".join(union_queries)
        
        # Create union table
        create_table_query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.simple_bills_union` AS
        {union_query}
        """
        
        try:
            job = self.bq_client.query(create_table_query)
            job.result()
            
            # Get row count
            count_query = f"SELECT COUNT(*) as total_rows FROM `{self.project_id}.{self.dataset_id}.simple_bills_union`"
            result = list(self.bq_client.query(count_query).result())[0]
            total_rows = result.total_rows
            
            logger.info(f"✓ Created union table with {total_rows} bills from {len(tables)} years")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error creating union table: {e}")
            return False
    
    def create_summary_view(self):
        """Create a summary view for quick analysis."""
        view_query = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.bills_summary` AS
        SELECT 
            data_year,
            state,
            COUNT(*) as total_bills,
            COUNT(CASE WHEN current_bill_status LIKE '%Pass%' OR current_bill_status LIKE '%Enact%' THEN 1 END) as passed_bills,
            COUNT(CASE WHEN current_bill_status LIKE '%Veto%' THEN 1 END) as vetoed_bills,
            COUNT(CASE WHEN current_bill_status LIKE '%Dead%' OR current_bill_status LIKE '%Fail%' THEN 1 END) as failed_bills,
            
            -- Calculate percentages
            ROUND(COUNT(CASE WHEN current_bill_status LIKE '%Pass%' OR current_bill_status LIKE '%Enact%' THEN 1 END) * 100.0 / COUNT(*), 1) as pass_rate,
            
            -- Most recent update
            MAX(last_updated) as data_last_updated
            
        FROM `{self.project_id}.{self.dataset_id}.simple_bills_union`
        WHERE state IS NOT NULL
        GROUP BY data_year, state
        ORDER BY data_year DESC, state
        """
        
        try:
            job = self.bq_client.query(view_query)
            job.result()
            logger.info("✓ Created bills summary view")
            return True
        except Exception as e:
            logger.error(f"✗ Error creating summary view: {e}")
            return False
    
    def run_pipeline(self):
        """Run the complete simplified pipeline."""
        logger.info("Starting simplified bills pipeline")
        
        # Find MDB files
        mdb_files = list(self.data_path.glob('*.mdb'))
        if not mdb_files:
            logger.error("No MDB files found")
            return
        
        logger.info(f"Found {len(mdb_files)} MDB files")
        
        # Process each file
        processed_years = []
        for mdb_file in sorted(mdb_files):
            logger.info(f"\nProcessing {mdb_file.name}")
            
            df_clean, data_year = self.extract_and_clean_bills(mdb_file)
            if df_clean is not None:
                success = self.load_to_bigquery(df_clean, data_year)
                if success:
                    processed_years.append(data_year)
        
        if processed_years:
            logger.info(f"\nProcessed years: {processed_years}")
            
            # Create union table
            if self.create_union_table():
                # Create summary view
                self.create_summary_view()
                
                logger.info("\n" + "="*60)
                logger.info("SIMPLIFIED PIPELINE COMPLETE!")
                logger.info("="*60)
                logger.info(f"✓ Processed {len(processed_years)} years: {processed_years}")
                logger.info(f"✓ Tables: simple_bills_union")
                logger.info(f"✓ Views: bills_summary")
                logger.info("Ready for basic analysis!")
        else:
            logger.error("No data was successfully processed")


def main():
    """Run the simplified pipeline."""
    PROJECT_ID = os.getenv('GCP_PROJECT_ID')
    DATASET_ID = os.getenv('BQ_DATASET_ID', 'legislative_tracker_staging')
    
    if not PROJECT_ID or PROJECT_ID == 'your-actual-project-id':
        logger.error("Please update GCP_PROJECT_ID in the .env file")
        return
    
    pipeline = SimpleBillsPipeline(PROJECT_ID, DATASET_ID)
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()