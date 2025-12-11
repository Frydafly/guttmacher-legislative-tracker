# Incident Log

This file tracks major incidents affecting BigQuery data and their resolutions.

## 2025-12-11: BigQuery Dataset Tables Deleted (Recovery Successful)

**What happened:** All tables in `legislative_tracker_historical`, `legislative_tracker_staging`, and `legislative_tracker_sandbox` datasets were empty (datasets existed but contained no tables)

**When discovered:** December 11, 2025

**Original deletion:** November 15, 2025, 11:13-11:25 AM UTC (based on `INFORMATION_SCHEMA.TABLE_STORAGE_TIMELINE_BY_PROJECT`)

**Cause:** Unknown - no DDL operations found in `JOBS_BY_PROJECT` history within 180-day retention window

**Impact:**
- 20,221 bills across 22 years (2002-2023) needed restoration
- Views and materialized tables deleted
- No active production impact (dashboards/Looker Studio would have been affected)

**Recovery method:**
1. Verified all source `.mdb` files still intact in `bigquery/data/`
2. Fixed authentication: ran `./setup_migration_env.sh`
3. Re-ran `archive/migrate.py` with explicit env var
4. Migration completed in 84.4 seconds

**Data loss:** None (all source `.mdb` files were intact)

**Time to recover:** ~15 minutes total (setup + migration + verification)

**Lessons learned:**
1. Script dependency resolution improved to search multiple locations for `.env`, `field_mappings.yaml`, and `data/` directory
2. Created `QUICK_RECOVERY.md` guide for faster future recovery
3. Documented symlinks in `archive/README.md`
4. Beyond 7-day time-travel window, full re-migration is required but fast (< 2 minutes)
5. Source `.mdb` files are critical - maintain backups

**Prevention measures added:**
- Quick recovery guide: `QUICK_RECOVERY.md`
- Backup script: `backup_snapshot.sh` (creates 7-day BigQuery snapshots)
- Incident logging: `INCIDENTS.md` (this file)
- Script improvements: Robust dependency resolution in `archive/migrate.py`

**Files modified during recovery:**
- `/Users/frydaguedes/Projects/guttmacher-legislative-tracker/.env` - Fixed placeholder value
- `bigquery/archive/migrate.py` - Enhanced dependency path resolution
- `bigquery/archive/README.md` - Documented symlinks and new search behavior

**Symlinks created:**
- `archive/.env` → `bigquery/.env`
- `archive/field_mappings.yaml` → `bigquery/field_mappings.yaml`
- `archive/data` → `bigquery/data`

---

## Template for Future Incidents

**What happened:**

**When discovered:**

**Original cause/time:**

**Cause:**

**Impact:**

**Recovery method:**

**Data loss:**

**Time to recover:**

**Lessons learned:**

**Prevention measures added:**
