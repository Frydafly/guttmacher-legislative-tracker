from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("Checking current BigQuery implementation state...")
print("=" * 80)

try:
    # List all tables and views in the dataset
    dataset_ref = client.dataset(dataset_id)
    tables = list(client.list_tables(dataset_ref))
    
    if not tables:
        print("❌ NO TABLES OR VIEWS FOUND IN DATASET!")
        print("The migration appears to have NOT been completed successfully.")
    else:
        print(f"✅ Found {len(tables)} objects in dataset:")
        
        table_count = 0
        view_count = 0
        
        for table in tables:
            table_info = client.get_table(table.reference)
            table_type = "VIEW" if table_info.table_type == "VIEW" else "TABLE"
            
            if table_type == "VIEW":
                view_count += 1
            else:
                table_count += 1
                
            print(f"  {table_type}: {table.table_id}")
            
            # Get row count for tables
            if table_type == "TABLE":
                try:
                    query = f"SELECT COUNT(*) as row_count FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{table.table_id}`"
                    result = client.query(query).result()
                    for row in result:
                        print(f"    Rows: {row.row_count:,}")
                except:
                    print(f"    Rows: Could not count")
        
        print(f"\nSummary: {table_count} tables, {view_count} views")
        
        # Check specifically for key objects
        print(f"\n{'='*50}")
        print("CHECKING KEY DELIVERABLES:")
        print(f"{'='*50}")
        
        key_objects = [
            "all_historical_bills_unified",
            "raw_data_tracking_by_year", 
            "looker_bills_dashboard",
            "looker_comprehensive_bills",
            "looker_state_summary",
            "looker_time_series"
        ]
        
        existing_tables = [table.table_id for table in tables]
        
        for obj in key_objects:
            if obj in existing_tables:
                print(f"✅ {obj} - EXISTS")
            else:
                print(f"❌ {obj} - MISSING")

except Exception as e:
    print(f"❌ Error accessing dataset: {e}")
    print("This suggests BigQuery permissions or connectivity issues.")