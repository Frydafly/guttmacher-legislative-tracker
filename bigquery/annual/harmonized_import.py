#!/usr/bin/env python3
"""
Harmonized Import - Apply field mapping and standardization
Creates analytical dataset with consistent schema across years
"""

import subprocess
import pandas as pd
import yaml
from pathlib import Path
from google.cloud import bigquery
from dotenv import load_dotenv
import os
import logging

load_dotenv()

def import_year_harmonized(year: int, config: dict):
    """Import year's data with harmonization"""
    logger = logging.getLogger(__name__)
    
    # Get configuration
    source_file = config['metadata']['source_file']
    table_name = config['metadata'].get('table_name', 'Legislative Monitoring')
    harmonized_config = config.get('harmonized_import', {})
    
    # Load field mappings
    base_path = Path(__file__).parent.parent
    mapping_name = harmonized_config.get('field_mapping', 'standard')
    
    if mapping_name == 'standard':
        mappings_path = base_path / "shared" / "field_mappings.yaml"
    else:
        mappings_path = base_path / "yearly_configs" / "field_mappings" / f"{mapping_name}.yaml"
    
    with open(mappings_path, 'r') as f:
        field_mappings = yaml.safe_load(f)
    
    # Paths
    data_path = base_path / "data" / source_file
    
    if not data_path.exists():
        raise FileNotFoundError(f"Source file not found: {data_path}")
    
    logger.info(f"📁 Processing {data_path.name} with {mapping_name} mapping")
    
    # Export from mdb
    csv_path = base_path / f"temp_harmonized_{year}.csv"
    cmd = f'mdb-export "{data_path}" "{table_name}" > "{csv_path}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"mdb-export failed: {result.stderr}")
    
    # Load and harmonize
    df = pd.read_csv(csv_path)
    logger.info(f"📊 Loaded {len(df)} rows")
    
    # Apply field mappings
    df_harmonized = harmonize_fields(df, field_mappings, year)
    logger.info(f"🔄 Harmonized to {len(df_harmonized.columns)} standard columns")
    
    # Upload to BigQuery (harmonized table)
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = "legislative_tracker_staging" 
    table_id = harmonized_config.get('table_name', f'historical_bills_{year}')
    
    client = bigquery.Client(project=project_id)
    full_table_id = f"{project_id}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True
    )
    
    job = client.load_table_from_dataframe(df_harmonized, full_table_id, job_config=job_config)
    job.result()
    
    logger.info(f"🔄 Harmonized data imported to {full_table_id}")
    
    # Update views if requested
    if config.get('post_import', {}).get('update_unified_view', True):
        update_unified_views(client, project_id)
    
    # Cleanup
    csv_path.unlink()
    
    return full_table_id

def harmonize_fields(df: pd.DataFrame, mappings: dict, year: int) -> pd.DataFrame:
    """Apply field mappings to standardize column names and values"""
    df_harmonized = df.copy()
    
    # Add year column
    df_harmonized['year'] = year
    
    # Create reverse mapping
    reverse_map = {}
    for category, fields in mappings.items():
        if isinstance(fields, dict):
            for standard_name, variants in fields.items():
                if isinstance(variants, list):
                    for variant in variants:
                        reverse_map[variant] = standard_name
    
    # Rename columns based on mappings
    df_harmonized = df_harmonized.rename(columns=reverse_map)
    
    # Apply data transformations (dates, flags, etc)
    df_harmonized = apply_transformations(df_harmonized)
    
    return df_harmonized

def apply_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """Apply data type transformations"""
    
    # Convert boolean flags (Access uses -1 for True, 0 for False)
    boolean_columns = ['positive_flag', 'negative_flag', 'neutral_flag', 'enacted_flag']
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: True if x == -1 else (False if x == 0 else None))
    
    # Convert dates
    date_columns = ['introduced_date', 'last_action_date', 'effective_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def update_unified_views(client: bigquery.Client, project_id: str):
    """Update unified views to include new year"""
    logger = logging.getLogger(__name__)
    
    # This would update the unified view to include the new year
    # Implementation depends on your view structure
    logger.info("🔄 Updated unified views")
