from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("🧹 CLEAN SLATE: Keeping only the 3 good views")
print("=" * 70)

# The 3 views we're keeping
keep_views = [
    'all_historical_bills_unified',
    'comprehensive_bills_authentic', 
    'raw_data_tracking_by_year'
]

# Get current objects
dataset_ref = client.dataset(dataset_id)
tables = list(client.list_tables(dataset_ref))

print("Current objects:")
views_to_drop = []
for table in tables:
    obj_type = "TABLE" if table.table_type == "BASE TABLE" else "VIEW"
    
    if obj_type == "VIEW" and table.table_id not in keep_views and not table.table_id.startswith('historical_bills_'):
        views_to_drop.append(table.table_id)
        print(f"  🗑️ WILL DROP: {table.table_id}")
    elif table.table_id in keep_views:
        print(f"  ✅ KEEPING: {table.table_id}")
    elif table.table_id.startswith('historical_bills_'):
        print(f"  📊 DATA TABLE: {table.table_id}")
    else:
        print(f"  ❓ OTHER: {table.table_id}")

print(f"\n📋 Plan: Drop {len(views_to_drop)} messy views, keep 3 good ones + data tables")

# Drop the messy views
for view_name in views_to_drop:
    try:
        drop_sql = f"DROP VIEW IF EXISTS `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{view_name}`"
        client.query(drop_sql).result()
        print(f"🗑️ Dropped: {view_name}")
    except Exception as e:
        print(f"❌ Failed to drop {view_name}: {e}")

print(f"\n✅ CLEAN SLATE ACHIEVED")
print("=" * 70)

# Verify our 3 essential views work
print("Testing the 3 essential views:")

for view_name in keep_views:
    try:
        test_query = f"SELECT COUNT(*) as count FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{view_name}`"
        result = client.query(test_query).result()
        count = next(result).count
        print(f"  ✅ {view_name}: {count:,} rows")
    except Exception as e:
        print(f"  ❌ {view_name}: Error - {e}")

# Final state
print(f"\n📊 FINAL DATASET STATE:")
final_tables = list(client.list_tables(dataset_ref))
data_tables = []
essential_views = []

for table in final_tables:
    if table.table_type == "BASE TABLE":
        data_tables.append(table.table_id)
    else:
        essential_views.append(table.table_id)

print(f"  📁 Data tables: {len(data_tables)} (historical_bills_YYYY)")
print(f"  🔗 Essential views: {len(essential_views)}")
for view in sorted(essential_views):
    print(f"    - {view}")

print(f"\n{'='*70}")
print("RECOMMENDATION FOR TEAM:")
print(f"{'='*70}")
print("""
🎯 Use these 3 views ONLY:

1. comprehensive_bills_authentic
   → For Google Sheets export (authentic data + dashboard helpers)
   
2. raw_data_tracking_by_year  
   → For understanding what was tracked when (field evolution)
   
3. all_historical_bills_unified
   → For advanced analysis (raw unified data)

All the messy looker_* views have been removed. 
Clean, simple, and focused on what actually works!
""")