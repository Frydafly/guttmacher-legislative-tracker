# Airtable Schema Snapshots

This directory contains schema snapshots from the Airtable base.

- **current_schema.md** - Human-readable schema (versioned in git)
- **airtable_schema_YYYY-MM-DD.json** - Dated JSON snapshots (not in git)

## How to Generate

To export a fresh schema snapshot:

```bash
cd bigquery
source venv/bin/activate
python etl/export_airtable_schema.py
```

The script will create both a markdown file and JSON file with the current date.
