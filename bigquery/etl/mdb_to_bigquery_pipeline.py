#!/usr/bin/env python3
"""
Complete pipeline to extract all MDB files and load to BigQuery.
Uses mdbtools for extraction since it's more reliable on Mac.
"""

import logging
import re
import subprocess
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MDBToBigQueryPipeline:
    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
        self.data_path = Path(__file__).parent.parent / 'data' / 'historical'
        self.staging_path = Path(__file__).parent.parent / 'data' / 'staging'
        self.staging_path.mkdir(exist_ok=True)
        
    def list_mdb_files(self):
        """Find all MDB files in the historical directory."""
        mdb_files = list(self.data_path.glob('*.mdb'))
        logger.info(f"Found {len(mdb_files)} MDB files")
        return sorted(mdb_files)
    
    def extract_tables_from_mdb(self, mdb_path):
        """Extract all tables from an MDB file using mdbtools."""
        # Get list of tables
        result = subprocess.run(
            ['mdb-tables', '-1', str(mdb_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error listing tables: {result.stderr}")
            return []
        
        tables = [t.strip() for t in result.stdout.strip().split('\n') if t.strip()]
        logger.info(f"Found {len(tables)} tables in {mdb_path.name}")
        
        extracted_files = []
        for table in tables:
            # Create safe filename
            safe_table_name = re.sub(r'[^\w\s-]', '', table).strip().replace(' ', '_')
            year = mdb_path.stem.split()[0]  # Extract year from filename
            output_file = self.staging_path / f"{year}_{safe_table_name}.csv"
            
            # Export table to CSV
            logger.info(f"Extracting {table} from {year}")
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    ['mdb-export', str(mdb_path), table],
                    stdout=f,
                    text=True
                )
                
            if result.returncode == 0:
                extracted_files.append({
                    'file': output_file,
                    'table': table,
                    'year': year,
                    'safe_name': safe_table_name
                })
            else:
                logger.error(f"Failed to extract {table}")
                
        return extracted_files
    
    def clean_dataframe(self, df, year):
        """Clean and standardize DataFrame for BigQuery."""
        # Add year column
        df['data_year'] = int(year)
        
        # Clean column names for BigQuery
        df.columns = [
            re.sub(r'[^\w]', '_', col.strip())
            .lower()
            .strip('_')
            for col in df.columns
        ]
        
        # Remove any completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Convert date-like columns
        for col in df.columns:
            if 'date' in col.lower() and df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
                    
        return df
    
    def create_bigquery_table(self, table_name, schema=None):
        """Create or update BigQuery table."""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            # Check if table exists
            self.bq_client.get_table(table_id)
            logger.info(f"Table {table_id} already exists")
            return True
        except:
            # Create new table
            if schema:
                table = bigquery.Table(table_id, schema=schema)
                self.bq_client.create_table(table)
                logger.info(f"Created table {table_id}")
            return True
    
    def load_csv_to_bigquery(self, csv_file, table_name, year):
        """Load CSV file to BigQuery."""
        # Read and clean data
        df = pd.read_csv(csv_file)
        df = self.clean_dataframe(df, year)
        
        # Generate table name
        bq_table_name = f"historical_{table_name}"
        table_id = f"{self.project_id}.{self.dataset_id}.{bq_table_name}"
        
        # Configure load job
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  # Append data
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION
            ],
            autodetect=True,
        )
        
        try:
            # Load data
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()
            
            logger.info(f"Loaded {len(df)} rows to {table_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading to BigQuery: {e}")
            return False
    
    def process_all_files(self):
        """Process all MDB files and load to BigQuery."""
        mdb_files = self.list_mdb_files()
        
        all_results = []
        for mdb_file in mdb_files:
            logger.info(f"\nProcessing {mdb_file.name}")
            
            # Extract tables
            extracted = self.extract_tables_from_mdb(mdb_file)
            
            # Load each table to BigQuery
            for item in extracted:
                success = self.load_csv_to_bigquery(
                    item['file'],
                    item['safe_name'],
                    item['year']
                )
                
                all_results.append({
                    'year': item['year'],
                    'table': item['table'],
                    'rows': len(pd.read_csv(item['file'])),
                    'success': success
                })
        
        return all_results
    
    def create_summary_views(self):
        """Create summary views in BigQuery."""
        views = [
            {
                'name': 'v_all_legislation',
                'query': """
                SELECT 
                    data_year,
                    state,
                    bill_number,
                    status,
                    title,
                    CAST(NULL AS STRING) as policy_area,
                    CURRENT_TIMESTAMP() as last_updated
                FROM `{project}.{dataset}.historical_state_legislative_table`
                ORDER BY data_year DESC, state, bill_number
                """
            },
            {
                'name': 'v_issue_areas',
                'query': """
                SELECT DISTINCT
                    specific_monitoring_category,
                    data_year,
                    COUNT(*) as year_count
                FROM `{project}.{dataset}.historical_specific_issue_areas`
                GROUP BY specific_monitoring_category, data_year
                ORDER BY specific_monitoring_category, data_year
                """
            }
        ]
        
        for view in views:
            view_id = f"{self.project_id}.{self.dataset_id}.{view['name']}"
            view_query = view['query'].format(
                project=self.project_id,
                dataset=self.dataset_id
            )
            
            # Create view
            view_ref = bigquery.Table(view_id)
            view_ref.view_query = view_query
            
            try:
                self.bq_client.create_table(view_ref)
                logger.info(f"Created view: {view['name']}")
            except Exception as e:
                if "Already Exists" in str(e):
                    # Update existing view
                    view_ref = self.bq_client.get_table(view_id)
                    view_ref.view_query = view_query
                    self.bq_client.update_table(view_ref, ['view_query'])
                    logger.info(f"Updated view: {view['name']}")
                else:
                    logger.error(f"Error creating view {view['name']}: {e}")


def main():
    """Run the complete pipeline."""
    # Load configuration from .env file
    import os

    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Configuration
    PROJECT_ID = os.getenv('GCP_PROJECT_ID')
    DATASET_ID = os.getenv('BQ_DATASET_ID', 'legislative_tracker_staging')
    
    if not PROJECT_ID or PROJECT_ID == 'your-actual-project-id':
        logger.error("Please update GCP_PROJECT_ID in the .env file")
        return
    
    # Initialize pipeline
    pipeline = MDBToBigQueryPipeline(PROJECT_ID, DATASET_ID)
    
    # Process all files
    logger.info("Starting MDB to BigQuery pipeline")
    results = pipeline.process_all_files()
    
    # Create summary views
    logger.info("\nCreating summary views")
    pipeline.create_summary_views()
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*60)
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        logger.info(
            f"{status} {result['year']} - {result['table']}: "
            f"{result['rows']} rows"
        )
    
    success_count = sum(1 for r in results if r['success'])
    logger.info(f"\nTotal: {success_count}/{len(results)} tables loaded successfully")


if __name__ == "__main__":
    main()