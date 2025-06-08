# Historical Data Migration Guide

This is a **one-time migration** to import all historical .mdb files (2002-2024) into BigQuery for analysis in Looker Studio.

⏱️ **Estimated time**: 10-30 minutes depending on data size  
🎯 **Result**: All historical data ready for analysis in BigQuery

## Quick Start

### 1. Prerequisites

```bash
# Install mdbtools (Mac)
brew install mdbtools

# Install Python dependencies
cd bigquery
pip install -r requirements.txt

# Authenticate with Google Cloud
gcloud auth application-default login
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your project ID
# Replace 'your-actual-project-id' with your real GCP project ID
# Example: GCP_PROJECT_ID=guttmacher-legislative-tracker
```

### 3. Add Your Data

Copy all your .mdb files (2002-2024) to:

```zsh
data/
```

Example file names:

- `Legislative_Bills_2002.mdb`
- `guttmacher_data_2003.mdb`
- `bills_database_2004.mdb`
- etc.

**Note**: The script automatically extracts the year from filenames containing 4-digit years.

### 4. Run Migration

```bash
# Single command - migrates everything
python migration_pipeline.py
```

You'll see progress like this:

```zsh
🔍 Validating migration setup...
✅ mdbtools available
✅ BigQuery access confirmed
✅ Found 23 .mdb files for migration
📁 Processing Legislative_Bills_2002.mdb (2002)
Processing 2002: 100%|██████████| 3/3 [00:05<00:00, 1.85s/it]
✅ Processed 3/3 tables from 2002
...
🎉 HISTORICAL DATA MIGRATION COMPLETE!
```

## What It Does

1. ✅ **Validates setup** - checks tools, authentication, data
2. 📁 **Processes each .mdb file** - extracts tables, cleans data
3. 📊 **Loads to BigQuery** - creates tables by year and type
4. 🔗 **Creates union views** - combines all years for analysis
5. 📋 **Generates report** - shows what was migrated

## Output

### BigQuery Tables Created

- `historical_bills_YYYY` - Bills data for each year
- `historical_categories_YYYY` - Policy categories for each year

### BigQuery Views Created

- `all_historical_bills` - All bills from all years combined
- `all_historical_categories` - All categories from all years combined

## Connect to Looker Studio

After migration completes:

1. Go to Looker Studio
2. Create new data source
3. Select BigQuery
4. Choose your project → `legislative_tracker_historical` dataset
5. Use the views: `all_historical_bills` or `all_historical_categories`

## Troubleshooting

### "No .mdb files found"

- Make sure files are in `data/`
- Files should have .mdb extension

### "mdbtools not found"

```bash
# Mac
brew install mdbtools

# Linux
sudo apt-get install mdbtools
```

### "GCP_PROJECT_ID not configured"

- Edit `.env` file
- Set `GCP_PROJECT_ID=your-actual-project-id`

### "BigQuery access failed"

```bash
gcloud auth application-default login
```

## File Structure After Migration

```markdown
bigquery/
├── data/                    # Your .mdb files (2002-2024)
├── migration_pipeline.py    # ← The only script you need
├── migration.log            # Migration log file
└── .env                     # Your configuration
```

## What's Already Here

✅ **Sample Data Ready**: There are already 3 .mdb files in `data/`:

- `2002 state legislation (back end).mdb`
- `2003 state legislation (back end).mdb`
- `2004 state legislation (back end).mdb`

You can test the migration immediately with these files, then add more .mdb files for 2005-2024.

## Next Steps After Migration

1. **Test with current data** (2002-2004):

   ```bash
   python migration_pipeline.py
   ```

2. **Add remaining years** (2005-2024):
   - Copy additional .mdb files to `data/`
   - Run migration again to include new years

3. **Connect to Looker Studio**:
   - Use BigQuery dataset: `legislative_tracker_historical`
   - Start with views: `all_historical_bills`, `all_historical_categories`

## Need Help?

- **Migration log**: Check `migration.log` for detailed progress
- **Script output**: The migration provides real-time progress updates
- **BigQuery Console**: Verify tables at <https://console.cloud.google.com/bigquery>
