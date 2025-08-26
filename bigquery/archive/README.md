# Archive Directory - Historical Migration Script

## Purpose

This directory contains the **completed historical migration script** that was used once to migrate 22 years of data (2002-2024) from Access databases to BigQuery.

## What's Here

- **`migrate.py`** - The monolithic historical migration script
  - ✅ **STATUS**: Successfully completed migration of 2002-2024 data
  - ✅ **PURPOSE SERVED**: Loaded 22+ years, ~22,000 bills into BigQuery
  - 🚫 **DO NOT USE**: This script is retired and should not be run again

## Why It's Archived

### ✅ Mission Accomplished
- Successfully migrated all historical data (2002-2024)
- Created harmonized schema across 22+ years  
- Built unified views and materialized tables
- Established field mappings and data quality tracking

### ❌ Wrong Tool for Ongoing Work
- **Overkill**: Re-processes ALL 22 years every time (takes ~90 minutes)
- **Monolithic**: One massive script doing everything
- **Historical focus**: Designed for one-time migration, not annual updates

## What to Use Instead

### For Annual Updates (2025, 2026, etc.)
```bash
# Use the new annual pipeline
python3 annual/add_year.py --year 2025
```

### For Data Analysis
```sql
-- Query the data that migrate.py created
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
```

## When You Might Reference This

### ✅ Good Reasons to Look at `migrate.py`:
- **Understanding field mappings**: See how historical schema harmonization worked
- **Debugging data issues**: Check how specific edge cases were handled  
- **Learning from approach**: Reference for building similar migration scripts
- **Documenting decisions**: Understanding why certain choices were made

### ❌ Bad Reasons to Use `migrate.py`:
- Adding new years (use `annual/add_year.py` instead)
- Re-running migration (the data is already there!)
- Making schema changes (use the annual pipeline)

## The Bottom Line

**Think of this like a construction crew that built your house:**
- ✅ The house is built and you live in it (the data is in BigQuery)  
- ✅ You keep the blueprints for reference (the migration script is archived)
- ❌ You don't call the construction crew to add a new room (use the annual pipeline instead)

---

**This script served its purpose perfectly. It's kept for historical reference and learning, but should not be used for ongoing work.**