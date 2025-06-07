#!/usr/bin/env python3
"""
Extract data from Access .mdb files and load to BigQuery staging tables.

Requirements:
    pip install -r ../requirements.txt
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
from google.cloud import bigquery

# Try to import pyodbc, provide helpful message if not available
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("WARNING: pyodbc not available. See setup.md for installation instructions.")
    print("You can still use CSV export method.")

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDBToBigQueryPipeline:
    def __init__(self, mdb_path, project_id, dataset_id):
        """
        Initialize pipeline for extracting MDB data to BigQuery.
        
        Args:
            mdb_path: Path to .mdb file
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.mdb_path = mdb_path
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
        
    def connect_to_mdb(self):
        """Connect to Access database."""
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={self.mdb_path};'
        )
        try:
            return pyodbc.connect(conn_str)
        except Exception as e:
            logger.error(f"Failed to connect to MDB: {e}")
            # Try alternative driver for Mac/Linux
            conn_str = f'DRIVER={{MDBTools}};DBQ={self.mdb_path};'
            return pyodbc.connect(conn_str)
    
    def list_tables(self):
        """List all tables in the MDB file."""
        conn = self.connect_to_mdb()
        cursor = conn.cursor()
        tables = []
        
        for table_info in cursor.tables(tableType='TABLE'):
            # Skip system tables
            if not table_info.table_name.startswith('MSys'):
                tables.append(table_info.table_name)
        
        conn.close()
        return tables
    
    def extract_table_to_dataframe(self, table_name):
        """Extract a table from MDB to pandas DataFrame."""
        conn = self.connect_to_mdb()
        
        try:
            # Use brackets for table names with spaces
            query = f'SELECT * FROM [{table_name}]'
            df = pd.read_sql(query, conn)
            logger.info(f"Extracted {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error extracting {table_name}: {e}")
            return None
        finally:
            conn.close()
    
    def clean_column_names(self, df):
        """Clean column names for BigQuery compatibility."""
        # Replace spaces and special characters
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('[^A-Za-z0-9_]', '', regex=True)
        df.columns = df.columns.str.lower()
        return df
    
    def infer_schema(self, df):
        """Infer BigQuery schema from DataFrame."""
        schema = []
        
        for column in df.columns:
            dtype = df[column].dtype
            
            if pd.api.types.is_integer_dtype(dtype):
                bq_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                bq_type = "FLOAT"
            elif pd.api.types.is_bool_dtype(dtype):
                bq_type = "BOOLEAN"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                bq_type = "TIMESTAMP"
            else:
                bq_type = "STRING"
            
            schema.append(bigquery.SchemaField(column, bq_type))
        
        return schema
    
    def load_to_bigquery(self, df, table_name, write_disposition="WRITE_TRUNCATE"):
        """Load DataFrame to BigQuery."""
        # Clean column names
        df = self.clean_column_names(df)
        
        # Create table reference
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name.lower().replace(' ', '_')}"
        
        # Configure load job
        job_config = bigquery.LoadJobConfig(
            schema=self.infer_schema(df),
            write_disposition=write_disposition,
        )
        
        try:
            # Load data
            job = self.bq_client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()  # Wait for job to complete
            
            logger.info(f"Loaded {len(df)} rows to {table_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading to BigQuery: {e}")
            return False
    
    def extract_all_tables(self, tables_to_extract=None):
        """Extract all tables from MDB to BigQuery."""
        tables = self.list_tables()
        
        if tables_to_extract:
            tables = [t for t in tables if t in tables_to_extract]
        
        logger.info(f"Found {len(tables)} tables to extract")
        
        results = {}
        for table in tables:
            logger.info(f"Processing table: {table}")
            
            # Extract data
            df = self.extract_table_to_dataframe(table)
            if df is not None:
                # Load to BigQuery
                success = self.load_to_bigquery(df, table)
                results[table] = {
                    'rows': len(df),
                    'success': success
                }
            else:
                results[table] = {
                    'rows': 0,
                    'success': False
                }
        
        return results


def main():
    """Example usage of the pipeline."""
    # Configuration
    MDB_PATH = "path/to/your/historical_data.mdb"
    PROJECT_ID = "your-gcp-project"
    DATASET_ID = "legislative_tracker_staging"
    
    # Initialize pipeline
    pipeline = MDBToBigQueryPipeline(MDB_PATH, PROJECT_ID, DATASET_ID)
    
    # List available tables
    tables = pipeline.list_tables()
    print(f"Available tables: {tables}")
    
    # Extract all tables
    results = pipeline.extract_all_tables()
    
    # Print summary
    print("\nExtraction Summary:")
    for table, result in results.items():
        status = "✓" if result['success'] else "✗"
        print(f"{status} {table}: {result['rows']} rows")


if __name__ == "__main__":
    main()