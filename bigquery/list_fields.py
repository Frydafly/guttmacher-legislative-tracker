from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
table = client.get_table('guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified')

print('Available fields:')
for field in sorted([f.name for f in table.schema]):
    print(f'  - {field}')