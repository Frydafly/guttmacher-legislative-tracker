#!/usr/bin/env python3
"""
Raw Archive Import - Preserve original database structure
No field mapping, no harmonization, pure historical preservation
"""

import subprocess
import pandas as pd
from pathlib import Path
from google.cloud import bigquery
from dotenv import load_dotenv
import os
import logging

load_dotenv()

def archive_year_raw(year: int, config: dict):
    """Archive year's data in original form"""
    logger = logging.getLogger(__name__)
    
    # Get configuration
    source_file = config['metadata']['source_file']
    table_name = config['metadata'].get('table_name', 'Legislative Monitoring')
    raw_config = config.get('raw_import', {})
    
    # Paths
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data" / source_file
    
    if not data_path.exists():
        raise FileNotFoundError(f"Source file not found: {data_path}")
    
    logger.info(f"📁 Processing {data_path.name}")
    
    # Handle different file formats
    if data_path.suffix.lower() in ['.mdb', '.accdb']:
        # Export from Access database
        csv_path = base_path / f"temp_raw_{year}.csv"
        cmd = f'mdb-export "{data_path}" "{table_name}" > "{csv_path}"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"mdb-export failed: {result.stderr}")
        
        df = pd.read_csv(csv_path)
        # Cleanup temp file
        csv_path.unlink()
        
    elif data_path.suffix.lower() == '.csv':
        # Direct CSV import (Airtable exports, etc.)
        df = pd.read_csv(data_path)
        logger.info("📊 Direct CSV import (no mdb-export needed)")
        
    else:
        raise ValueError(f"Unsupported file format: {data_path.suffix}")
    
    logger.info(f"📊 Loaded {len(df)} rows with {len(df.columns)} original columns")
    
    # Add metadata columns
    df['import_year'] = year
    df['import_date'] = pd.Timestamp.now()
    df['source_file'] = source_file
    
    # Upload to BigQuery (raw table)
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = "legislative_tracker_staging"  # Raw data goes to staging
    table_id = raw_config.get('table_name', f'raw_historical_{year}')
    
    client = bigquery.Client(project=project_id)
    full_table_id = f"{project_id}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True
    )
    
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result()  # Wait for completion
    
    logger.info(f"📦 Raw data archived to {full_table_id}")
    
    # Cleanup
    csv_path.unlink()
    
    return full_table_id
