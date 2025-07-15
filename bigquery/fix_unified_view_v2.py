#!/usr/bin/env python3
"""
Fix the unified view to handle different column orders
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()

def get_table_columns(client, dataset_id, table_name):
    """Get column names for a specific table."""
    query = f"""
    SELECT column_name 
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """
    
    results = client.query(query).result()
    return [row.column_name for row in results]

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
    
    print(f"Found {len(tables)} historical tables")
    
    # Get column names from the first table as reference
    reference_columns = get_table_columns(client, dataset_id, tables[0])
    print(f"Using column order from {tables[0]}")
    
    # Create SELECT statement with explicit column names (quoted for safety)
    column_selects = [f"  `{col}`" for col in reference_columns]
    
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
    
    # Create materialized table (without clustering for now)
    create_table_sql = f"""
    CREATE OR REPLACE TABLE `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_materialized` AS
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
    total_bills = 0
    for row in results:
        print(f"  {row.data_year}: {row.bills:,} bills")
        total_bills += row.bills
    
    print(f"\nTotal: {total_bills:,} bills across {len(tables)} years")

if __name__ == "__main__":
    create_explicit_unified_view()