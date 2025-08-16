# Utilities

Quick helper scripts for checking and validating BigQuery data.

## 🚀 Active Utilities (3)

### 1. `check_data.py`
Quick health check of your BigQuery tables
```bash
python utilities/check_data.py

# Shows:
# - Row counts
# - Table sizes
# - Positive/restrictive bill counts
```

### 2. `compare_datasets.py`
Compare sandbox vs production data
```bash
python utilities/compare_datasets.py

# Useful for:
# - Validating new pipeline results
# - Checking data consistency
```

### 3. `validate_views.py` 
Check if BigQuery views are working
```bash
python utilities/validate_views.py

# Shows:
# - View status
# - Last update times
# - Any errors
```

## 📦 Archived Utilities

Moved to `utilities/archive/`:
- Historical migration scripts
- One-time data fixes
- Old analysis scripts

These were for the original .mdb migration and aren't needed for day-to-day operations.

## Usage

All utilities require:
```bash
# From bigquery/ directory
source venv/bin/activate  # If using virtual env
python utilities/script_name.py
```

## When to Use These

- **After loading new data**: Run `check_data.py` to verify
- **Before production load**: Run `compare_datasets.py` to validate
- **If views seem stale**: Run `validate_views.py`

For regular data loading, use the main pipeline:
```bash
python run_pipeline.py --config production
```