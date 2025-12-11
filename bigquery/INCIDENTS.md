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

## 2025-12-11: Looker Studio Dashboard Error - Missing Views (Documentation Issue)

**What happened:** Looker Studio dashboard showed "Data Set Configuration Error" for "Data Quality Report" chart attempting to use `tracking_completeness_matrix` view

**When discovered:** December 11, 2025 (same day as data recovery)

**Original cause/time:** Views were documented but never actually implemented

**Cause:** Documentation described 5 "Field Tracking Status Views" that were planned but never created. Migration script only creates 3 core views, not 8.

**Impact:**
- One dashboard chart broken (admin/analyst chart, not end-user facing)
- No data loss - core analytical views functional
- Dashboard confusion about what views exist

**Missing views (documented but non-existent):**
1. `tracking_completeness_matrix`
2. `realistic_field_tracking_by_year`
3. `field_tracking_completeness_by_year`
4. `corrected_policy_tracking`
5. `bills_with_consolidated_intent`

**Root cause:** Documentation drift - docs described aspirational state, not actual implementation

**Recovery method:**
1. Analysis confirmed views never existed in codebase
2. All functionality available through existing `raw_data_tracking_by_year` view
3. Created replacement SQL query: `sql/data_quality_report.sql`
4. Updated documentation to match reality
5. Created dashboard fix guide: `LOOKER_DASHBOARD_FIX.md`

**Data loss:** None - no views were actually deleted, they never existed

**Time to resolve:** 2 hours (analysis + fix documentation + create alternatives)

**Lessons learned:**
1. Documentation should describe actual state, not planned features
2. Missing views weren't needed - existing views sufficient
3. Data quality analysis better done ad-hoc via BigQuery Console than fixed dashboard charts
4. "Simple > Perfect" validated - team never built these because they weren't needed

**Resolution actions:**
- Updated `2002_2024_Historical_Migration.md` to remove non-existent view references
- Created `sql/data_quality_report.sql` for ad-hoc data quality analysis
- Created `LOOKER_DASHBOARD_FIX.md` with 3 options to fix dashboard
- Recommended removing broken chart (admin-only functionality)

**Files created/modified:**
- `bigquery/sql/data_quality_report.sql` - New query for data quality analysis
- `bigquery/LOOKER_DASHBOARD_FIX.md` - Dashboard repair guide
- `bigquery/2002_2024_Historical_Migration.md` - Corrected documentation
- `bigquery/INCIDENTS.md` - This entry

**Recommended user action:** Remove broken chart or update to use `raw_data_tracking_by_year`

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
