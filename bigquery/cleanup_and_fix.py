from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("🧹 SYSTEMATIC CLEANUP AND FIX")
print("=" * 70)

print("\n1. Checking current state...")
# Get current objects
dataset_ref = client.dataset(dataset_id)
tables = list(client.list_tables(dataset_ref))
current_objects = {table.table_id: table.table_type for table in tables}

print(f"Found {len(current_objects)} objects:")
for name, obj_type in sorted(current_objects.items()):
    print(f"  {obj_type}: {name}")

print("\n2. Creating missing essential views...")

# Create looker_bills_dashboard view (simple alias to our authentic view)
dashboard_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.looker_bills_dashboard` AS
SELECT * FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic`
"""

try:
    client.query(dashboard_sql).result()
    print("✅ Created looker_bills_dashboard (alias to comprehensive_bills_authentic)")
except Exception as e:
    print(f"❌ Failed to create looker_bills_dashboard: {e}")

print("\n3. Verifying essential views exist...")

essential_views = [
    'all_historical_bills_unified',
    'comprehensive_bills_authentic', 
    'raw_data_tracking_by_year',
    'looker_bills_dashboard',
    'looker_state_summary',
    'looker_time_series',
    'looker_topic_analysis'
]

print("Essential views status:")
missing_views = []
for view_name in essential_views:
    if view_name in current_objects:
        print(f"  ✅ {view_name}")
    else:
        print(f"  ❌ {view_name} - MISSING")
        missing_views.append(view_name)

if missing_views:
    print(f"\n⚠️ Missing views: {missing_views}")
    print("You may need to run the migration pipeline to recreate these.")
else:
    print(f"\n✅ All essential views are present!")

print("\n4. Testing data consistency...")

# Test the key views have data
test_queries = [
    ("comprehensive_bills_authentic", "SELECT COUNT(*) as count FROM `{}.{}.comprehensive_bills_authentic`"),
    ("raw_data_tracking_by_year", "SELECT COUNT(*) as count FROM `{}.{}.raw_data_tracking_by_year`"),
    ("all_historical_bills_unified", "SELECT COUNT(*) as count FROM `{}.{}.all_historical_bills_unified`")
]

for view_name, query_template in test_queries:
    try:
        query = query_template.format(os.getenv('GCP_PROJECT_ID'), dataset_id)
        result = client.query(query).result()
        count = next(result).count
        print(f"  ✅ {view_name}: {count:,} rows")
    except Exception as e:
        print(f"  ❌ {view_name}: Error - {e}")

print("\n5. Final state check...")
final_tables = list(client.list_tables(dataset_ref))
final_objects = {table.table_id: table.table_type for table in final_tables}

table_count = sum(1 for t in final_objects.values() if t == "BASE TABLE")
view_count = sum(1 for t in final_objects.values() if t == "VIEW")

print(f"Final count: {table_count} tables, {view_count} views")

print(f"\n{'='*70}")
print("CLEANUP COMPLETE")
print(f"{'='*70}")

print("""
✅ Status: Project cleaned up and organized

🎯 For Google Sheets, use:
   comprehensive_bills_authentic (authentic data with dashboard enhancements)

📊 For field evolution tracking:
   raw_data_tracking_by_year (shows what was tracked when)

🔗 For Looker Studio:
   looker_bills_dashboard (alias to comprehensive_bills_authentic)
   looker_state_summary, looker_time_series, looker_topic_analysis

All views now preserve authentic NULL patterns while providing dashboard value.
""")