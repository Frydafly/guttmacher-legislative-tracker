# Quick Start Guide - BigQuery Historical Data Pipeline v2.0

Get up and running with the pipeline in under 10 minutes.

## ⚡ Express Setup

### 1. Prerequisites Check

```bash
# Verify Python 3.9+
python --version  # Should show 3.9 or higher

# Verify mdbtools (install if missing)
mdb-ver || brew install mdbtools

# Verify Google Cloud access
gcloud auth list  # Should show authenticated account
```

### 2. Project Setup

```bash
# Navigate to bigquery directory
cd /path/to/guttmacher-legislative-tracker/bigquery

# Create and activate virtual environment
python -m venv venv && source venv/bin/activate

# Install dependencies (takes ~2 minutes)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Update GCP_PROJECT_ID with your actual project
```

### 3. Data Preparation

```bash
# Copy your .mdb files to the data directory
cp /path/to/your/*.mdb data/historical/

# Verify files are detected
ls -la data/historical/*.mdb
```

### 4. Run Pipeline

```bash
# Quick validation (30 seconds)
python etl/consolidated_pipeline.py --validate

# Process data (2-3 minutes for 3 years)
python etl/consolidated_pipeline.py
```

### 5. Verify Results

```bash
# Check BigQuery dataset
gcloud bq ls --project_id=YOUR_PROJECT_ID legislative_tracker_staging

# View summary
python -c "
from google.cloud import bigquery
import os
from dotenv import load_dotenv
load_dotenv()

client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
query = '''
SELECT 
  data_year,
  COUNT(*) as bills,
  COUNT(DISTINCT state) as states
FROM \`{}.{}.historical_bills_union\`
GROUP BY data_year 
ORDER BY data_year
'''.format(os.getenv('GCP_PROJECT_ID'), os.getenv('BQ_DATASET_ID'))

for row in client.query(query).result():
    print(f'{row.data_year}: {row.bills} bills from {row.states} states')
"
```

## 🎯 Expected Output

After successful completion, you should see:

```
✓ 2002: 177 bills from X states
✓ 2003: 110 bills from X states  
✓ 2004: 107 bills from X states
Total: 394 bills processed
```

## 🔗 Next Steps

1. **Connect Looker Studio** to your BigQuery dataset
2. **Start with** the `v_bills_summary` view for dashboards
3. **Explore** the union tables for detailed analysis
4. **Add more data** by copying additional .mdb files

```text
Expected Output:
✓ 2002: 177 bills from X states
✓ 2003: 110 bills from X states  
✓ 2004: 107 bills from X states
Total: 394 bills processed
```

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `mdbtools not found` | `brew install mdbtools` |
| `BigQuery access denied` | `gcloud auth application-default login` |
| `No .mdb files found` | Copy files to `data/historical/` |
| `Project ID not set` | Update `GCP_PROJECT_ID` in `.env` file |

## ⏱️ Typical Timing

- **Setup**: 5 minutes
- **Data processing**: 2-3 minutes (3 years of data)
- **BigQuery operations**: 1-2 minutes
- **Total**: Under 10 minutes for complete setup and processing

Ready to analyze your historical legislative data! 🎉