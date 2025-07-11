from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = 'legislative_tracker_historical'

print("Dropping views that obscured raw data availability...")
print("=" * 70)

# Drop the previous views that focused on populated vs NULL instead of raw availability
views_to_drop = [
    'field_population_by_year',
    'field_true_false_progression', 
    'data_quality_summary'
]

for view_name in views_to_drop:
    try:
        query = f'DROP VIEW IF EXISTS `{os.getenv("GCP_PROJECT_ID")}.{dataset_id}.{view_name}`'
        client.query(query).result()
        print(f'✅ Dropped view: {view_name}')
    except Exception as e:
        print(f'❌ Error dropping {view_name}: {str(e)}')

print('\n🗑️ Cleaned up views that obscured raw data availability')
print("Focus is now on what was actually collected each year, not harmonized data")