#!/usr/bin/env python3
"""
Quick data checker for BigQuery tables
"""

import sys
from google.cloud import bigquery
from dotenv import load_dotenv
import os

def check_table(dataset_id, table_id):
    """Check basic stats for a table"""
    load_dotenv()
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID', 'guttmacher-legislative-tracker'))
    
    try:
        # Get table info
        table_ref = f"{client.project}.{dataset_id}.{table_id}"
        table = client.get_table(table_ref)
        
        print(f"\n📊 Table: {table_ref}")
        print(f"   Rows: {table.num_rows:,}")
        print(f"   Size: {table.num_bytes / 1024 / 1024:.2f} MB")
        print(f"   Created: {table.created}")
        
        # Sample query - handle INT64 boolean fields
        query = f"""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT state) as states,
            SUM(CAST(positive AS INT64)) as positive_bills,
            SUM(CAST(restrictive AS INT64)) as restrictive_bills
        FROM `{table_ref}`
        """
        
        result = client.query(query).result()
        for row in result:
            print(f"\n   Summary:")
            print(f"   - Total records: {row.total:,}")
            print(f"   - States: {row.states}")
            print(f"   - Positive bills: {row.positive_bills:,}")
            print(f"   - Restrictive bills: {row.restrictive_bills:,}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🔍 BigQuery Data Checker")
    print("=" * 50)
    
    # Check sandbox
    print("\n1️⃣ SANDBOX DATA:")
    check_table('legislative_tracker_sandbox', 'bills_test')
    
    # Check production
    print("\n2️⃣ PRODUCTION DATA:")
    check_table('legislative_tracker_historical', 'all_historical_bills_unified')
    
    print("\n" + "=" * 50)
    print("✅ Check complete")

if __name__ == "__main__":
    main()