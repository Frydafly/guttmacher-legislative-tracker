from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset = client.dataset('legislative_tracker_historical')
tables = list(client.list_tables(dataset))

print(f'Tables created: {len(tables)}')
for t in sorted(tables, key=lambda x: x.table_id):
    print(f'  - {t.table_id}')