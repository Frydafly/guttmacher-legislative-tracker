# Quick Recovery Guide

If BigQuery tables are accidentally deleted, follow these steps to restore data.

## Within 7 Days of Deletion

BigQuery automatically keeps table snapshots for 7 days. Use time-travel to restore:

```bash
# Restore specific table from snapshot
bq cp --snapshot \
  project:dataset.table@SNAPSHOT_TIME \
  project:dataset.table_restored

# Example: Restore table as it was 24 hours ago (86400000 ms)
bq cp \
  guttmacher-legislative-tracker:legislative_tracker_historical.all_historical_bills_unified@-86400000 \
  guttmacher-legislative-tracker:legislative_tracker_historical.all_historical_bills_unified
```

**Time:** Minutes
**Pros:** Fast, preserves exact state
**Cons:** Only works within 7 days

## Beyond 7 Days (Full Re-Migration)

If more than 7 days have passed, re-run the historical migration:

### Step 1: Setup Environment (5 min)
```bash
cd /Users/frydaguedes/Projects/guttmacher-legislative-tracker/bigquery
./setup_migration_env.sh
```

This script:
- Configures correct GCP project and account
- Sets up Application Default Credentials
- Verifies BigQuery access
- Checks all dependencies

### Step 2: Run Migration (60-90 min)
```bash
# From bigquery directory
GCP_PROJECT_ID=guttmacher-legislative-tracker python3 archive/migrate.py
```

**What gets restored:**
- 22 year tables: `historical_bills_2002` through `historical_bills_2023`
- Unified view: `all_historical_bills_unified`
- Comprehensive view: `comprehensive_bills_authentic`
- Data quality view: `raw_data_tracking_by_year`
- Total: ~20,000+ bills across 22 years

### Step 3: Verify Results (5 min)
```bash
# Check table count
bq ls guttmacher-legislative-tracker:legislative_tracker_historical

# Query to verify data
bq query --use_legacy_sql=false \
"SELECT
  COUNT(*) as total_bills,
  COUNT(DISTINCT data_year) as years_covered,
  MIN(data_year) as earliest,
  MAX(data_year) as latest
FROM \`guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified\`"
```

**Expected Results:**
- Total bills: ~20,000-22,000
- Years covered: 22 (2002-2023)
- All year tables exist

## Prerequisites

**Required files in `/bigquery/data/`:**
- 22+ `.mdb` and `.accdb` files (2002-2024)
- These are the source data files
- If missing: Check backups or contact data owner

**Required setup:**
- gcloud CLI installed
- mdbtools installed (`brew install mdbtools`)
- Python environment with dependencies
- BigQuery access via `fryda.guedes@gmail.com`

## Troubleshooting

### "Permission denied" errors
**Solution:** Re-run `./setup_migration_env.sh`

### "Field mappings not found"
**Solution:** Verify symlinks exist in archive/ directory, or script will auto-find them

### "No database files found"
**Solution:** Verify `.mdb`/`.accdb` files exist in `bigquery/data/`

### "Invalid GCP_PROJECT_ID"
**Solution:** Set explicitly: `GCP_PROJECT_ID=guttmacher-legislative-tracker python3 archive/migrate.py`

## Prevention: Before Risky Changes

Create a snapshot before making major changes:

```bash
cd /Users/frydaguedes/Projects/guttmacher-legislative-tracker/bigquery
./backup_snapshot.sh
```

This creates a 7-day BigQuery snapshot (free, no storage cost).

## When to Use This Guide

**Use for:**
- Accidental table deletions
- Dataset corruption
- Testing gone wrong
- Disaster recovery

**Don't use for:**
- Adding new years (use `annual/add_year.py` instead)
- Schema changes (modify pipeline, not re-migrate)
- Data analysis (query existing tables)

## Summary

| Scenario | Time | Method |
|----------|------|--------|
| Deleted < 7 days ago | Minutes | BigQuery time-travel |
| Deleted > 7 days ago | 60-90 min | Re-run migrate.py |
| Annual update (2025+) | 10-20 min | Use annual/add_year.py |

**Last tested:** December 11, 2025 (successful restoration of all data)
