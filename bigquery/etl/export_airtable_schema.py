#!/usr/bin/env python3
"""
Simple script to export Airtable schema for documentation purposes.
Run manually when you want to capture current schema state.

Usage:
    cd bigquery
    source venv/bin/activate
    python etl/export_airtable_schema.py

Credentials loaded from bigquery/.env file
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configuration
API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')

if not API_KEY or not BASE_ID:
    print("❌ Error: AIRTABLE_API_KEY and AIRTABLE_BASE_ID not found")
    print("\nAdd them to: bigquery/.env")
    print("\nGet your API key: https://airtable.com/account")
    print("Get your Base ID: From your base URL (starts with 'app...')")
    print("\nSee: .github/scripts/README.md for setup instructions")
    exit(1)

# Fetch base schema
print("🔍 Fetching Airtable schema...")
url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
    exit(1)

schema = response.json()

# Create output directory
os.makedirs('docs/schema', exist_ok=True)

# Save full JSON
timestamp = datetime.now().strftime("%Y-%m-%d")
json_path = f'docs/schema/airtable_schema_{timestamp}.json'

with open(json_path, 'w') as f:
    json.dump(schema, f, indent=2)

print(f"✅ Saved full schema to: {json_path}")

# Create human-readable markdown
md_path = 'docs/schema/current_schema.md'
with open(md_path, 'w') as f:
    f.write(f"# Airtable Schema Snapshot\n\n")
    f.write(f"**Captured**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
    f.write(f"**Base ID**: `{BASE_ID}`\n\n")

    for table in schema['tables']:
        f.write(f"## {table['name']}\n\n")
        f.write(f"**Table ID**: `{table['id']}`\n\n")
        f.write(f"### Fields\n\n")
        f.write("| Field Name | Type | Description |\n")
        f.write("|------------|------|-------------|\n")

        for field in table['fields']:
            field_type = field['type']
            field_name = field['name']

            # Add type details if available
            description = ""
            if field_type == 'singleSelect' and 'options' in field:
                choices = [opt['name'] for opt in field['options']['choices']]
                description = f"Options: {', '.join(choices[:3])}{'...' if len(choices) > 3 else ''}"
            elif field_type == 'multipleSelects' and 'options' in field:
                choices = [opt['name'] for opt in field['options']['choices']]
                description = f"Options: {', '.join(choices[:3])}{'...' if len(choices) > 3 else ''}"
            elif field_type == 'formula' and 'options' in field:
                description = "Formula field"
            elif field_type == 'multipleRecordLinks' and 'options' in field:
                linked_table = field['options'].get('linkedTableId', 'Unknown')
                description = f"Links to table {linked_table}"

            f.write(f"| {field_name} | {field_type} | {description} |\n")

        f.write("\n")

print(f"✅ Saved readable schema to: {md_path}")
print("\n📋 Next steps:")
print("1. Review docs/schema/current_schema.md")
print("2. Compare with existing documentation")
print("3. Update docs if field names or types changed")
print("4. Commit the schema snapshot to git")
