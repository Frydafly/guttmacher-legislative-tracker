#!/usr/bin/env python3
"""
Compare data between sandbox and production
Useful for validating new pipeline results
"""

from google.cloud import bigquery
from dotenv import load_dotenv
import os
import pandas as pd

def compare_datasets():
    load_dotenv()
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID', 'guttmacher-legislative-tracker'))
    
    print("📊 Dataset Comparison")
    print("=" * 60)
    
    # Query both datasets
    sandbox_query = """
    SELECT 
        state,
        COUNT(*) as bill_count,
        SUM(CAST(positive AS INT64)) as positive,
        SUM(CAST(restrictive AS INT64)) as restrictive
    FROM `legislative_tracker_sandbox.bills_test`
    WHERE state IS NOT NULL
    GROUP BY state
    ORDER BY bill_count DESC
    LIMIT 10
    """
    
    prod_query = """
    SELECT 
        state,
        COUNT(*) as bill_count,
        SUM(CAST(intent_positive AS INT64)) as positive,
        SUM(CAST(intent_restrictive AS INT64)) as restrictive  
    FROM `legislative_tracker_historical.all_historical_bills_unified`
    WHERE data_year = 2024 AND state IS NOT NULL
    GROUP BY state
    ORDER BY bill_count DESC
    LIMIT 10
    """
    
    print("\n🧪 SANDBOX (New Pipeline):")
    sandbox_df = client.query(sandbox_query).to_dataframe()
    print(sandbox_df.to_string())
    
    print("\n📦 PRODUCTION (2024 Data):")
    try:
        prod_df = client.query(prod_query).to_dataframe()
        print(prod_df.to_string())
    except:
        print("   No 2024 data in production yet")
    
    print("\n" + "=" * 60)
    print("Use this to verify your new pipeline matches expected results")

if __name__ == "__main__":
    compare_datasets()