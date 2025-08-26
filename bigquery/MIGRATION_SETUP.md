# BigQuery Migration Setup Guide

This guide ensures you can run the annual migration script reliably every year.

## Quick Setup (Run This First!)

```bash
cd bigquery
./setup_migration_env.sh
```

This script automatically handles all the setup steps below.

## What the Setup Script Does

### 1. **Authentication Setup**
- Sets correct Google Cloud account: `fryda.guedes@gmail.com`
- Sets correct project: `guttmacher-legislative-tracker`
- **Fixes Application Default Credentials quota project** (the key issue we had)

### 2. **Permission Verification**
- Tests BigQuery access
- Verifies you can create jobs and tables
- Lists available datasets

### 3. **Tool Dependencies**
- Checks for `gcloud` CLI
- Installs `mdbtools` if missing (macOS with Homebrew)
- Verifies Python packages

### 4. **Configuration**
- Creates/updates `.env` file with correct project settings
- Validates field mappings are present

## Manual Setup (If Script Fails)

### Step 1: Install Dependencies
```bash
# macOS
brew install --cask google-cloud-sdk
brew install mdbtools

# Python packages
pip install -r requirements.txt
```

### Step 2: Fix Authentication (Most Important!)
```bash
# Set correct account and project
gcloud config set account fryda.guedes@gmail.com
gcloud config set project guttmacher-legislative-tracker

# The critical fix - reset Application Default Credentials
gcloud auth application-default revoke --quiet
gcloud auth application-default login --project=guttmacher-legislative-tracker
```

### Step 3: Verify Setup
```bash
python3 test_access.py
```

## Running the Migration

### Annual Migration (Full)
```bash
python3 migrate.py
```

### Test Migration Results
```bash
python3 migrate.py --test
```

### Clean Up Old Objects
```bash
python3 migrate.py --cleanup
```

## Troubleshooting

### Permission Error: "User does not have bigquery.jobs.create permission"
**Solution**: Run the setup script again, specifically this part:
```bash
gcloud auth application-default revoke --quiet
gcloud auth application-default login --project=guttmacher-legislative-tracker
```

### "Dataset not found" Error
**Solution**: Check your `.env` file has the correct dataset:
```
GCP_PROJECT_ID=guttmacher-legislative-tracker
BQ_DATASET_ID=legislative_tracker_historical
```

### "mdbtools not found"
**Solution**: Install mdbtools:
```bash
# macOS
brew install mdbtools

# Ubuntu/Linux
sudo apt-get install mdbtools
```

### Schema/Column Type Errors
**Solution**: The migration handles schema evolution automatically. If you get UNION errors, the existing materialized view may need to be updated first.

## File Locations

- **Migration Script**: `migrate.py`
- **Setup Script**: `setup_migration_env.sh`
- **Configuration**: `.env` (created by setup)
- **Field Mappings**: `field_mappings.yaml`
- **Database Files**: `data/*.mdb` and `data/*.accdb`

## Expected Results

A successful migration will:
1. Process 20+ years of data (2002-2024+)
2. Load 20,000+ individual bills
3. Create individual year tables: `historical_bills_YYYY`
4. Update unified views and materialized tables
5. Generate analytics views for Looker Studio

## What Changed This Year

**Root Cause of Permission Issue**: The Application Default Credentials were using the wrong quota project. Even though you had Owner permissions, the Python BigQuery client couldn't create jobs because it was authenticating against a different project's quota.

**The Fix**: Re-authenticating ADC with the `--project` flag ensures the quota project matches the target project.

## Next Year's Process

1. **Before migration**: Run `./setup_migration_env.sh`
2. **Add new year's data**: Copy new `.mdb/.accdb` files to `data/` directory
3. **Run migration**: `python3 migrate.py`
4. **Verify results**: Check BigQuery console for new year's data
5. **Update documentation**: Note any new fields or schema changes

This setup ensures the migration "just works" every year without permission headaches!