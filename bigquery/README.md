# Guttmacher Legislative Tracker - BigQuery Migration

A simple one-time migration pipeline to extract historical legislative data from Access (.mdb) files and load it into BigQuery for Looker Studio analysis.

## 🎯 What This Does

1. **Extracts** data from historical Access .mdb files (2002-2024)
2. **Cleans** and standardizes the data for BigQuery
3. **Loads** data directly to BigQuery tables
4. **Creates** union views combining all years
5. **Verifies** data was successfully loaded

## 📁 Project Structure

```
bigquery/
├── data/                       # Your .mdb files (2002-2024)
├── migration_pipeline.py       # Single migration script
├── looker_studio_views.sql     # Optional dashboard views
├── requirements.txt            # Python dependencies
├── MIGRATION_GUIDE.md          # Step-by-step instructions
├── .env                        # Your GCP configuration
└── migration.log               # Migration history
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install mdbtools for .mdb file processing
brew install mdbtools                # macOS
# sudo apt-get install mdbtools      # Linux
```

### 2. Google Cloud Setup

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Copy environment template and configure
cp .env.example .env
# Edit .env and set: GCP_PROJECT_ID=your-actual-project-id
```

### 3. Add Your Data

```bash
# Copy .mdb files to data directory
cp /path/to/your/*.mdb data/
```

### 4. Run Migration

```bash
# Single command migrates everything
python migration_pipeline.py
```

## 📊 What Gets Created

### BigQuery Tables
- `historical_bills_YYYY` - Bills data for each year
- `historical_categories_YYYY` - Policy categories for each year

### BigQuery Views (Ready for Looker Studio)
- `all_historical_bills` - All bills from all years combined
- `all_historical_categories` - All categories from all years combined
- `looker_bills_dashboard` - Enhanced view with calculated fields

## 🔍 Verification Built-In

The migration automatically verifies data was loaded by querying BigQuery:

```
🔍 BIGQUERY VERIFICATION:
✅ Bills in BigQuery: 394 rows across 3 years
✅ Categories in BigQuery: 127 rows across 3 years
```

## 📈 Connect to Looker Studio

1. Go to Looker Studio
2. Create new data source → BigQuery
3. Select your project → `legislative_tracker_historical` dataset
4. Choose view: `looker_bills_dashboard` (recommended) or `all_historical_bills`

## 🛠️ Requirements

### System Requirements
- Python 3.8+
- mdbtools (for .mdb file processing)
- Google Cloud access

### Python Dependencies (from requirements.txt)
- `pandas>=2.0.0` - Data processing
- `google-cloud-bigquery>=3.0.0` - BigQuery integration
- `python-dotenv>=1.0.0` - Environment configuration
- `tqdm>=4.0.0` - Progress bars

### Google Cloud Requirements
- BigQuery API enabled
- Service account with BigQuery admin permissions
- Or user account with BigQuery access

## 🔧 Troubleshooting

### "mdbtools not found"
```bash
brew install mdbtools        # macOS
sudo apt install mdbtools    # Linux
```

### "GCP_PROJECT_ID not configured"
Edit `.env` file and set your actual project ID:
```
GCP_PROJECT_ID=your-actual-project-id
```

### "BigQuery access failed"
```bash
gcloud auth application-default login
```

### "No .mdb files found"
Ensure files are in `data/` directory with `.mdb` extension.

## 📋 Adding More Years

To add more .mdb files later:

1. Copy new .mdb files to `data/` directory
2. Run `python migration_pipeline.py` again
3. The script will process new files and update union views

## 🔒 Security Notes

### What's Committed to Git
✅ Source code and configuration templates  
✅ Documentation and requirements

### What's NOT Committed  
❌ Historical .mdb files (your sensitive data)  
❌ .env file (your credentials)  
❌ Log files with execution details

## 📞 Need Help?

- **Migration Guide**: See `MIGRATION_GUIDE.md` for detailed instructions
- **Logs**: Check `migration.log` for detailed progress
- **Verification**: The script automatically verifies data in BigQuery
- **Test Run**: The migration includes sample data (2002-2004) for testing

## 🎯 Example Output

```
🎉 HISTORICAL DATA MIGRATION COMPLETE!
⏱️  Total Time: 28.1 seconds
📁 Files Processed: 3
📅 Years: [2002, 2003, 2004]
📋 Total Bills: 394
📂 Total Categories: 127

🔍 BIGQUERY VERIFICATION:
✅ Bills in BigQuery: 394 rows across 3 years
✅ Categories in BigQuery: 127 rows across 3 years

🎯 BigQuery Dataset: your-project.legislative_tracker_historical
📊 Ready for Looker Studio connection!
```