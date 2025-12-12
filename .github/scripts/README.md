# Airtable Schema Export

Simple script to document your Airtable schema.

## Location

**Script moved to**: `bigquery/etl/export_airtable_schema.py`

Uses the existing BigQuery virtual environment - no separate setup needed!

## When to Run

Run this whenever:
- You add/remove fields in Airtable
- You rename fields
- You want to verify docs match reality
- Before major script updates

**Frequency**: As needed (maybe quarterly)

## Setup

### 1. Add Airtable credentials to .env file

```bash
cd bigquery
cp .env.example .env
```

Edit `.env` and add:
```
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXX
```

**Get your API key**: https://airtable.com/account

**Get your Base ID**: From your Airtable URL (the part starting with `app`)

## Usage

```bash
# Activate the existing venv
cd bigquery
source venv/bin/activate

# Install requests if not already installed
pip install -r requirements.txt

# Run the export
python etl/export_airtable_schema.py
```

That's it! Uses the same venv as BigQuery operations.

## Output

Creates two files:

**1. `docs/schema/airtable_schema_YYYY-MM-DD.json`**
- Full JSON schema (not committed to git)

**2. `docs/schema/current_schema.md`**
- Human-readable markdown
- **Committed to git** for version tracking
- Use this to verify docs match reality

## What to Do After Running

1. **Review** `docs/schema/current_schema.md`
2. **Compare** with documentation
3. **Update docs** if field names or types changed
4. **Update scripts** if CONFIG objects need changes
5. **Commit** the schema snapshot

```bash
git add docs/schema/current_schema.md
git commit -m "Update Airtable schema snapshot"
```

## Why Use the BigQuery venv?

✅ Simpler - reuse existing setup
✅ All Python tools in one place
✅ Same dependencies already installed
✅ Follows project conventions

---

*Simple and pragmatic. Run when needed, not automated.*
