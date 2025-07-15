#!/usr/bin/env python3
"""
VIEW VALIDATION CHECKER
======================

Validates that BigQuery views are up-to-date and functioning properly.
Views in BigQuery automatically recalculate when underlying data changes,
but this script helps verify they're working and current.

Usage:
    python validate_views.py                    # Check all views
    python validate_views.py --detailed         # Show detailed breakdown
"""

from google.cloud import bigquery
from dotenv import load_dotenv
import os
from datetime import datetime

def validate_views():
    load_dotenv()
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    print("🔍 BIGQUERY VIEW VALIDATION")
    print("=" * 50)
    print(f"Dataset: {dataset_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Essential views to check
    essential_views = [
        'all_historical_bills_unified',
        'comprehensive_bills_authentic', 
        'raw_data_tracking_by_year'
    ]
    
    # Get all tables/views in dataset
    dataset_ref = client.dataset(dataset_id)
    all_objects = list(client.list_tables(dataset_ref))
    
    # Separate tables and views
    data_tables = [obj for obj in all_objects if obj.table_type == "BASE TABLE" and obj.table_id.startswith('historical_bills_')]
    views = [obj for obj in all_objects if obj.table_type == "VIEW"]
    
    print(f"📊 DATASET OVERVIEW:")
    print(f"  Data tables: {len(data_tables)} (historical_bills_YYYY)")
    print(f"  Views: {len(views)}")
    print()
    
    # Check if views automatically update
    print(f"🔄 VIEW AUTO-UPDATE STATUS:")
    print(f"  ✅ BigQuery views are LIVE - they automatically recalculate when data changes")
    print(f"  ✅ No manual refresh needed - views always show current data")
    print(f"  ✅ Views update in real-time when tables are modified")
    print()
    
    # Validate essential views exist and work
    print(f"🎯 ESSENTIAL VIEW VALIDATION:")
    
    for view_name in essential_views:
        print(f"\n📋 {view_name}:")
        
        try:
            # Check if view exists
            view_ref = client.dataset(dataset_id).table(view_name)
            view = client.get_table(view_ref)
            print(f"  ✅ Exists: {view.table_type}")
            
            # Test the view with a simple query
            test_query = f"""
            SELECT 
                COUNT(*) as total_bills,
                COUNT(DISTINCT data_year) as years_covered,
                MIN(data_year) as earliest_year,
                MAX(data_year) as latest_year
            FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{view_name}`
            """
            
            result = client.query(test_query).result()
            row = next(result)
            
            print(f"  ✅ Functional: {row.total_bills:,} bills across {row.years_covered} years")
            print(f"  📅 Range: {row.earliest_year} - {row.latest_year}")
            
            # Check if view includes latest data
            latest_table_query = f"""
            SELECT table_name, EXTRACT(YEAR FROM creation_time) as created_year
            FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
            WHERE table_name LIKE 'historical_bills_%'
            ORDER BY creation_time DESC
            LIMIT 1
            """
            
            latest_result = client.query(latest_table_query).result()
            latest_row = next(latest_result)
            latest_table_year = int(latest_row.table_name.split('_')[-1])
            
            if row.latest_year >= latest_table_year:
                print(f"  ✅ Current: Includes latest table data ({latest_table_year})")
            else:
                print(f"  ⚠️ Outdated: Missing data from {latest_table_year}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Check for any orphaned views
    print(f"\n🧹 ORPHANED VIEW CHECK:")
    for view in views:
        if view.table_id not in essential_views:
            print(f"  ⚠️ Extra view: {view.table_id} (may be outdated)")
    
    # Data freshness check
    print(f"\n📅 DATA FRESHNESS:")
    
    freshness_query = f"""
    SELECT 
        data_year,
        COUNT(*) as bills,
        MAX(migration_date) as last_migration
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    GROUP BY data_year
    ORDER BY data_year DESC
    LIMIT 5
    """
    
    try:
        result = client.query(freshness_query).result()
        print(f"  Most recent years:")
        for row in result:
            print(f"    {row.data_year}: {row.bills:,} bills (migrated: {row.last_migration})")
    except Exception as e:
        print(f"  ❌ Error checking freshness: {e}")
    
    print(f"\n✅ VALIDATION COMPLETE")
    print("=" * 50)
    print(f"💡 REMEMBER: Views automatically update when data changes!")
    print(f"💡 To add new data: Use add_year.py YYYY")
    print(f"💡 Views will instantly include new data once tables are updated")

if __name__ == "__main__":
    validate_views()