# Archive Directory - Historical Documentation

## Purpose

This directory contains historical migration scripts, completed incident documentation, and archived proposals for the BigQuery pipeline.

## What's Here

### Migration Script (Completed)

- **`migrate.py`** - The monolithic historical migration script
  - ✅ **STATUS**: Successfully completed migration of 2002-2024 data
  - ✅ **PURPOSE SERVED**: Loaded 22+ years, ~22,000 bills into BigQuery
  - 🚫 **DO NOT USE**: This script is retired and should not be run again

### Historical Migration Documentation

- **`2002_2024_Historical_Migration.md`** - Documentation of the one-time historical data migration project
  - Complete record of the initial migration process
  - Useful for understanding historical decisions
  - Archived because migration is complete

### Incident Reports (Resolved)

- **`FIELD_FIX_SUMMARY.md`** - Summary of field mapping fixes from December 2024
- **`DASHBOARD_DATA_QUALITY_CHART.md`** - Dashboard data quality chart incident documentation
- **`DASHBOARD_FIX_ACTION.md`** - Dashboard fix action plan (completed)

These documents are kept for historical reference but represent completed work.

### Architectural Proposals

- **`ARCHITECTURE_PROPOSAL.md`** - Original architecture proposal for BigQuery pipeline
  - Historical context for system design decisions
  - Archived because system is now implemented

## Why It's Archived

### ✅ Mission Accomplished
- Successfully migrated all historical data (2002-2024)
- Created harmonized schema across 22+ years  
- Built unified views and materialized tables
- Established field mappings and data quality tracking

### ❌ Wrong Tool for Ongoing Work
- **Overkill**: Re-processes ALL 22 years every time (takes ~90 minutes)
- **Monolithic**: One massive script doing everything
- **Historical focus**: Designed for one-time migration, not annual updates

## What to Use Instead

### For Annual Updates (2025, 2026, etc.)
```bash
# Use the new annual pipeline
python3 annual/add_year.py --year 2025
```

### For Data Analysis
```sql
-- Query the data that migrate.py created
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
```

## When You Might Reference This

### ✅ Good Reasons to Look at `migrate.py`:
- **Understanding field mappings**: See how historical schema harmonization worked
- **Debugging data issues**: Check how specific edge cases were handled  
- **Learning from approach**: Reference for building similar migration scripts
- **Documenting decisions**: Understanding why certain choices were made

### ❌ Bad Reasons to Use `migrate.py`:
- Adding new years (use `annual/add_year.py` instead)
- Re-running migration (the data is already there!)
- Making schema changes (use the annual pipeline)

## The Bottom Line

**Think of this like a construction crew that built your house:**
- ✅ The house is built and you live in it (the data is in BigQuery)  
- ✅ You keep the blueprints for reference (the migration script is archived)
- ❌ You don't call the construction crew to add a new room (use the annual pipeline instead)

---

## Technical Note: Dependencies (Updated Dec 2025)

The script now intelligently searches for its dependencies in multiple locations:

**Configuration files:**
- Searches for `.env` in: `archive/.env` → `bigquery/.env`
- Searches for `field_mappings.yaml` in: `archive/` → `bigquery/` → `bigquery/shared/`
- Searches for `data/` directory in: `archive/data` → `bigquery/data`

**Sym links in place** (for convenience):
- `archive/.env` → `bigquery/.env`
- `archive/field_mappings.yaml` → `bigquery/field_mappings.yaml`
- `archive/data` → `bigquery/data`

These symlinks exist so the script can run from either the `archive/` directory or the `bigquery/` directory. This makes recovery operations more flexible if ever needed again.

**If you need to run this (you shouldn't!):**
```bash
cd /path/to/bigquery
./setup_migration_env.sh  # Fix authentication
GCP_PROJECT_ID=guttmacher-legislative-tracker python3 archive/migrate.py
```

---

**This script served its purpose perfectly. It's kept for historical reference and learning, but should not be used for ongoing work.**