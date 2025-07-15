#!/usr/bin/env python3
"""
Fix the unified view to handle different column orders
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

def get_standardized_columns():
    """Get the standardized column set from field mappings."""
    with open('field_mappings.yaml', 'r') as f:
        mappings = yaml.safe_load(f)
    
    # Get all possible standard fields
    standard_fields = set()
    for category in mappings.values():
        if isinstance(category, dict):
            standard_fields.update(category.keys())
    
    # Add the data_year field which is added during processing
    standard_fields.add('data_year')
    
    return sorted([str(f) for f in standard_fields])

def create_explicit_unified_view():
    """Create unified view with explicit column selection."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Get all historical bill tables
    query = f"""
    SELECT table_name FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'historical_bills_%' 
    ORDER BY table_name
    """
    
    results = client.query(query).result()
    tables = [row.table_name for row in results]
    
    if not tables:
        print("No historical tables found")
        return
    
    print(f"Found {len(tables)} historical tables:")
    for table in tables:
        print(f"  - {table}")
    
    # Get the standard column set
    standard_columns = get_standardized_columns()
    
    # Create SELECT statement with explicit column names
    column_selects = []
    for col in standard_columns:
        column_selects.append(f"  {col}")
    
    # Build union parts with explicit column selection
    union_parts = []
    for table in tables:
        select_stmt = f"SELECT\n" + ",\n".join(column_selects) + f"\nFROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{table}`"
        union_parts.append(select_stmt)
    
    # Create the unified view
    create_view_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified` AS
    {' UNION ALL '.join(union_parts)}
    """
    
    print("\n🔄 Creating unified view with explicit column selection...")
    try:
        job = client.query(create_view_sql)
        job.result()
        print("✅ Successfully created unified view")
    except Exception as e:
        print(f"❌ Failed to create unified view: {e}")
        return
    
    # Create materialized table
    create_table_sql = f"""
    CREATE OR REPLACE TABLE `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_materialized` 
    CLUSTER BY (state, data_year) AS
    {' UNION ALL '.join(union_parts)}
    """
    
    print("\n🔄 Creating materialized table...")
    try:
        job = client.query(create_table_sql)
        job.result(timeout=600)
        print("✅ Successfully created materialized table")
    except Exception as e:
        print(f"❌ Failed to create materialized table: {e}")
        return
    
    # Test the view
    test_query = f"""
    SELECT 
        data_year,
        COUNT(*) as bills
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    GROUP BY data_year
    ORDER BY data_year
    """
    
    print("\n📊 Testing unified view:")
    results = client.query(test_query).result()
    for row in results:
        print(f"  {row.data_year}: {row.bills} bills")

if __name__ == "__main__":
    create_explicit_unified_view()