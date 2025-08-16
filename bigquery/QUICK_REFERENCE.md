# Quick Reference - BigQuery Pipeline

## Common Commands

### Load Current Airtable Export
```bash
# 1. Export from Airtable as CSV
# 2. Place in data/ folder
# 3. Run:
python run_pipeline.py --source csv --file data/your_export.csv
```

### Load to Production
```bash
# Edit config to use production dataset
python run_pipeline.py --config production
```

### Test Without Loading
```bash
python test_new_pipeline.py
```

## Configuration Files

### Test/Sandbox
- **File**: `config/test_sandbox.json`
- **Dataset**: `legislative_tracker_sandbox`
- **Table**: `bills_test`

### Production (create this)
```json
{
  "source": {
    "type": "csv",
    "config": {
      "file_path": "data/airtable_export.csv"
    }
  },
  "destination": {
    "project_id": "guttmacher-legislative-tracker",
    "dataset_id": "legislative_tracker_historical",
    "table_id": "bills_current"
  }
}
```

## Key Fields Now Mapped

### Intent Classification
- `positive` - Positive/supportive bills
- `neutral` - Neutral bills
- `restrictive` - Restrictive bills

### Policy Areas
- `abortion` - Abortion-related
- `contraception` - Contraception-related
- `medication_abortion` - Medication abortion
- `telehealth` - Telehealth services
- `family_planning` - Family planning
- `period_products` - Period products
- `incarceration` - Incarceration-related
- `sex_ed` - Sex education
- `youth` - Youth-related

### Status Fields
- `introduced` - Bill introduced
- `enacted` - Bill enacted
- `vetoed` - Bill vetoed
- `dead` - Bill dead
- `passed_first_chamber` - Passed first chamber
- `passed_legislature` - Passed legislature

## BigQuery Queries

### Check Data Quality
```sql
SELECT 
  COUNT(*) as total,
  COUNT(DISTINCT state) as states,
  SUM(CAST(positive AS INT64)) as positive_bills,
  SUM(CAST(restrictive AS INT64)) as restrictive_bills
FROM `legislative_tracker_sandbox.bills_test`
```

### Find Recent Bills
```sql
SELECT 
  state, bill_number, bill_description,
  positive, neutral, restrictive
FROM `legislative_tracker_sandbox.bills_test`
WHERE enacted = 1
ORDER BY state
```

## Troubleshooting

### Encoding Error
- **Problem**: "utf-8 codec can't decode"
- **Solution**: Pipeline auto-detects and uses latin1 encoding

### Duplicate Columns
- **Problem**: "Field X already exists"
- **Solution**: Fixed in harmonizer - duplicates get renamed

### Permission Error
- **Problem**: "Access Denied"
- **Solution**: 
  ```bash
  gcloud auth application-default login
  gcloud config set project guttmacher-legislative-tracker
  ```

## Clean Up Test Data
```bash
# Remove test table
bq rm -t legislative_tracker_sandbox.bills_test

# Remove entire sandbox (careful!)
bq rm -r -d legislative_tracker_sandbox
```

## Still Using Old Pipeline?

Your original pipeline still works:
```bash
python migrate.py  # For historical .mdb files
```

Both pipelines can coexist!