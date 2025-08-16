# Safe Testing Guide - Try Without Breaking Anything

## ✅ Your Current Setup is Protected

**Nothing in the new pipeline touches your existing data:**
- `migrate.py` - Still works exactly the same
- Historical tables - Unchanged
- BigQuery views - Unchanged  
- Field mappings - Still in place

## 🧪 Test the New Pipeline Safely

### 1. Dry Run Test (No BigQuery Required)
```bash
# Test all components without touching BigQuery
python test_new_pipeline.py

# Output:
# ✅ CSV Extractor: Connection validated
# ✅ Harmonizer: Transformed columns
# ✅ Would load X rows to BigQuery (but didn't)
```

### 2. Test with Real CSV (Still Safe)
```bash
# Export from Airtable, then test
python test_new_pipeline.py --real-csv data/your_export.csv
```

### 3. Load to Sandbox Dataset (Not Production)
```bash
# Uses legislative_tracker_sandbox dataset (not your production data)
python run_pipeline.py --config test_sandbox

# This creates a SEPARATE test table you can delete anytime
```

## 🛡️ Safety Features

### Separate Test Dataset
The test config uses `legislative_tracker_sandbox` dataset:
- Completely separate from `legislative_tracker_historical`
- Safe to create, test, and delete
- Won't appear in your production views

### Validation Mode
```bash
# Just check if everything is configured correctly
python test_new_pipeline.py --validate
```

### Your Escape Hatch
```bash
# If anything goes wrong, your original pipeline still works:
python migrate.py  # Works exactly as before
```

## 📝 Testing Checklist

- [ ] Run `test_new_pipeline.py` - Confirms code works
- [ ] Test with sample CSV - Validates data processing
- [ ] Load to sandbox dataset - Tests BigQuery integration
- [ ] Compare results with production - Verify accuracy
- [ ] Delete sandbox when done - Clean up test data

## 🚦 When You're Ready

Only after testing, you can:
1. Use the new pipeline for real Airtable exports
2. Keep using old pipeline for historical data
3. Both pipelines coexist peacefully

## 💡 Common Test Scenarios

### Test Incremental Updates
```bash
# First load
python run_pipeline.py --config test_sandbox

# Add new data to CSV, then:
python run_pipeline.py --config test_sandbox --incremental
```

### Test Schema Changes
Edit `config/test_sandbox.json` to test different mappings without affecting production.

### Test Error Handling
```bash
# Test with bad data
echo "bad,data,here" > data/bad.csv
python run_pipeline.py --source csv --file data/bad.csv
# Should fail gracefully without breaking anything
```

## 🔧 Cleanup

When done testing:
```sql
-- In BigQuery console (optional)
DROP DATASET legislative_tracker_sandbox CASCADE;
```

Or just leave it - it costs nothing if empty!

---

**Remember**: The new pipeline is ADDITIVE. It doesn't replace or modify your existing setup until you explicitly choose to use it for production data.