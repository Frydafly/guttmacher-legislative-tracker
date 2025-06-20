# Guttmacher Legislative Tracker - BigQuery Migration

Complete migration pipeline for 20+ years (2005-2024) of legislative tracking data with schema harmonization and Looker Studio optimization.

## 🎯 What This Does

1. **Migrates** historical .mdb/.accdb files (2005-2024) to BigQuery
2. **Harmonizes** varying database schemas using field mapping configuration  
3. **Creates** comprehensive Looker Studio table optimized for analysis
4. **Validates** migration success with built-in testing

## 📁 Project Structure

```
bigquery/
├── data/                    # Your database files (2005-2024)
│   ├── *.mdb               # Legacy Access databases (2005-2019)
│   └── *.accdb             # Modern Access databases (2020-2024)
├── migrate.py              # Single migration script (everything!)
├── field_mappings.yaml     # Schema harmonization configuration
├── requirements.txt        # Python dependencies 
├── .env                    # Your GCP configuration
└── migration.log          # Migration history
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install mdbtools for database processing
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
# Copy database files to data directory
cp /path/to/your/*.mdb data/
cp /path/to/your/*.accdb data/
```

### 4. Run Migration

```bash
# Run complete migration
python migrate.py

# Test migration results
python migrate.py --test

# Clean up old objects (if needed)
python migrate.py --cleanup

# Create just Looker table (if unified view exists)
python migrate.py --looker-only
```

## 📊 What Gets Created

### BigQuery Objects

**Individual Year Tables:**
- `historical_bills_YYYY` - Harmonized bills data for each year (2005-2024)

**Unified Data:**
- `all_historical_bills_unified` - All years combined with consistent schema

**Looker Studio Table (Primary):**
- `looker_comprehensive_bills` - **THE** table for all analysis
  - 📊 All bill data with calculated fields
  - 🗺️ Geographic groupings (state, region)  
  - 📅 Time period groupings
  - ⚖️ Status progressions and success metrics
  - 🏷️ Policy area classifications and counts
  - 📝 All topics/subpolicies
  - 💡 Analytical flags and helpers

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