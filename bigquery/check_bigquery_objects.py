#!/usr/bin/env python3
"""Check what BigQuery objects were created."""

import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()
project_id = os.getenv('GCP_PROJECT_ID')
dataset_id = 'legislative_tracker_historical'

client = bigquery.Client(project=project_id)

# List all tables and views
query = f"""
SELECT 
    table_name,
    table_type,
    creation_time,
    last_modified_time
FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
ORDER BY table_name
"""

print('Tables and Views in legislative_tracker_historical dataset:')
print('=' * 80)

results = client.query(query).result()
for row in results:
    print(f'{row.table_type}: {row.table_name}')