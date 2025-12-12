# Runbook: Troubleshooting Guide

This runbook provides step-by-step solutions for common issues with the Guttmacher Legislative Tracker system.

!!! info "Quick Reference"
    Jump to: [Airtable Issues](#airtable-issues) | [Script Failures](#script-failures) | [Data Quality](#data-quality-issues) | [BigQuery](#bigquery-issues) | [Emergency](#emergency-procedures)

## Airtable Issues

### Issue: Automation Failed to Run

**Symptoms**: Scheduled automation didn't execute at expected time

**Diagnosis**:
1. Check Airtable Automations tab
2. Look for automation status (enabled/disabled)
3. Review automation run history for error messages

**Solution**:

**Step 1**: Verify automation is enabled
```
Automations tab → Find automation → Check toggle is ON
```

**Step 2**: Check run history
```
Click automation → "Run history" → Review recent runs
```

**Step 3**: Common causes & fixes

| Error Message | Cause | Fix |
|--------------|-------|-----|
| "No records match trigger" | Trigger conditions not met | Review trigger formula/conditions |
| "Script timeout" | Script took >30 seconds | See [Script Timeout](#issue-script-timeout) |
| "Permission denied" | Base permissions changed | Verify automation has base access |
| "Rate limit exceeded" | Too many API calls | Add delays between batch operations |

**Step 4**: Manual run test
- Click "Test run" or "Run now"
- Monitor console output
- Check if records are processed correctly

---

### Issue: Script Timeout

**Symptoms**: "Script execution exceeded time limit" error

**Diagnosis**:
- Script processes large dataset
- Infinite loop in code
- Inefficient queries

**Solution**:

**For large datasets**:
1. Add pagination to queries:
   ```javascript
   // Instead of loading all records
   const allRecords = await table.selectRecordsAsync();

   // Use views or filters to limit scope
   const view = table.getView('Current Year Only');
   const records = await view.selectRecordsAsync();
   ```

**For weekly/regular operations**:
1. Process incrementally (only new/changed records)
2. Use "Last Updated" filters
3. Batch operations in chunks of 50

**Immediate workaround**:
1. Run script on smaller subset
2. Process manually in batches
3. Contact technical team for optimization

---

### Issue: Field Name Mismatch

**Symptoms**: "Cannot read property of undefined" or unexpected null values

**Diagnosis**:
- Field was renamed in Airtable
- Script still references old field name
- CONFIG object out of sync

**Solution**:

**Step 1**: Identify the field
- Note the error message field name
- Check if field exists in Airtable base

**Step 2**: Update script CONFIG
```javascript
const CONFIG = {
  FIELD_NAMES: {
    BILL_ID: 'BillID',  // Verify this matches Airtable exactly
    STATE: 'State',      // Check capitalization
    // ...
  }
};
```

**Step 3**: Compare with Airtable
- Open table in Airtable
- Click field header
- Verify exact name (case-sensitive!)

**Step 4**: Update and redeploy
- Fix CONFIG in GitHub repo
- Commit changes
- Redeploy script per [Deployment Guide](deployment-guide.md)

---

## Script Failures

### Issue: Health Monitoring Script Failed

**Symptoms**: Weekly health check didn't run or reported errors

**Location**: `airtable-scripts/health-monitoring/`

**Diagnosis Checklist**:
- [ ] Check automation run history
- [ ] Verify System Monitor table exists
- [ ] Check if Bills table is accessible
- [ ] Review quality score thresholds

**Solution**:

**Step 1**: Check System Monitor table
```
Navigate to System Monitor table
Look for latest run record
Check error_message field if present
```

**Step 2**: Verify data sources
- Bills table should have records
- Required fields must exist:
  - BillID
  - State
  - Current Bill Status
  - Website Blurb
  - Intent

**Step 3**: Review quality score calculation
- Check if thresholds changed
- Verify weight values in CONFIG
- Ensure all metrics are calculable

**Step 4**: Manual run
```
Automations tab → Health Monitoring Weekly
Click "Run now"
Monitor console output
```

**Expected output**:
```
✅ Health Monitoring Complete
📊 Quality Score: 85.3
📈 Bills Tracked: 1,956
⚠️ Issues Found: 3
```

---

### Issue: Partner Email Report Script Failed

**Symptoms**: Bi-weekly report didn't send or has formatting errors

**Location**: `airtable-scripts/partner-email-report/`

**Critical Timeline**:
- Runs 1st and 15th of each month
- DO NOT debug during active run window (1st-3rd, 15th-17th)

**Diagnosis**:
1. Check run history for error message
2. Verify date filters are correct
3. Check if bills exist in query range

**Solution**:

**Step 1**: Verify date range
```javascript
// Script filters by action dates
// Check if current date range has bills
```

**Step 2**: Check email format
- HTML format may have issues
- Special characters need escaping
- Verify all required fields present

**Step 3**: Test with small dataset
- Manually limit to 5-10 bills
- Run script
- Verify output format

**Step 4**: Contact policy team
- Verify if they received report
- Check spam folders

**Rollback option**:
- Use previous month's report as template
- Generate manually if urgent
- Fix script after delivery deadline

---

### Issue: Website Export Script Failed

**Symptoms**: Export to Website Exports table incomplete or errored

**Location**: `airtable-scripts/website-export/`

**⚠️ HIGH PRIORITY** - Affects public website

**Diagnosis**:
1. Check export quality score (should be >95%)
2. Verify pre-flight validation passed
3. Check for missing website blurbs
4. Review data validation flags

**Solution**:

**Step 1**: Check pre-flight validation
```
Run script
Look for validation warnings:
- Missing website blurbs
- Invalid dates
- Missing required fields
```

**Step 2**: Fix data quality issues
```
Bills table → Filter for:
- Status = Enacted OR Vetoed
- Website Blurb = empty
Fill in missing blurbs
```

**Step 3**: Verify export scope
- Check year filter (current year only?)
- Verify status filters (enacted/vetoed)
- Confirm policy categorization complete

**Step 4**: Manual export verification
1. Run export script
2. Check Website Exports table
3. Verify record count matches expectations
4. Spot-check sample records for accuracy

**Emergency procedure**:
- If export corrupted Website Exports table
- See [Emergency: Data Deletion from Airtable](#emergency-data-deletion-from-airtable)

---

### Issue: Supersedes Detector Not Finding Duplicates

**Symptoms**: Known duplicate bills not flagged

**Location**: `airtable-scripts/supersedes-detector/`

**Note**: Experimental script, low priority

**Diagnosis**:
- Check if script is running at all
- Verify similarity threshold
- Review detection algorithm

**Solution**:
1. Confirm script is deployed and active
2. Check threshold settings (may be too strict)
3. Manually review suspected duplicates
4. Consider if feature is needed at all

---

## Data Quality Issues

### Issue: Quality Score Dropped Below 50

**Symptoms**: Health monitoring reports low quality score

**Impact**: Indicates systematic data problems

**Investigation Steps**:

**Step 1**: Identify problem areas
```
Check System Monitor table latest run:
- Which metrics scored low?
- How many bills affected?
- Trend over time?
```

**Step 2**: Common quality issues

| Low Metric | Likely Cause | Fix |
|------------|--------------|-----|
| Blurb completion | Missing website blurbs | Fill in enacted/vetoed bill blurbs |
| Date validity | Future dates or bad formats | Check Date Validation field, fix |
| Policy categorization | Missing Specific Policies | Categorize bills properly |
| Status accuracy | History not processed | Check History field format |

**Step 3**: Bulk fix process
1. Create view filtered by problem metric
2. Review affected bills
3. Fix systematically (don't skip around)
4. Re-run health monitoring
5. Verify score improved

**Step 4**: Prevent recurrence
- Train team on common errors
- Add validation to import process
- Update documentation if needed

---

### Issue: Bills Not Updating from StateNet Import

**Symptoms**: New StateNet imports not creating/updating Bills records

**Diagnosis**:
1. Check StateNet Raw Import table
   - Are new records appearing?
   - Are they linked to Bills records?

2. Check automation: "Process StateNet Import"
   - Is it enabled?
   - Check run history

**Solution**:

**Step 1**: Verify import process
```
StateNet Raw Import table
Check Import Time field (recent?)
Check Linked Bill Record (populated?)
```

**Step 2**: Test automation
```
Create test record in StateNet Raw Import
Watch if Bills record created/updated
Check automation run history
```

**Step 3**: Common mapping issues
- StateNet Bill ID format changed
- Jurisdiction field empty
- Bill Type not recognized
- Summary field missing

**Step 4**: Manual processing
If automation stuck:
1. Note StateNet Bill ID
2. Search Bills table for matching record
3. Manually update fields from import
4. Flag for technical review

---

### Issue: Formula Fields Not Calculating

**Symptoms**: Date extraction formulas showing blank or "0"

**Affected Fields**:
- Introduction Date Formula
- Last Action Date Formula
- Enacted Date Formula
- Current Bill Status

**Diagnosis**:
- History field format changed
- StateNet history format changed
- Formula regex not matching

**Solution**:

**Step 1**: Check History field format
```
Expected format:
MM/DD/YYYY (Chamber) Action text
Example:
01/15/2024 (H) Introduced and referred to committee
```

**Step 2**: Verify formula still valid
- See [Airtable Formulas Reference](../reference/airtable-formulas.md)
- Check if StateNet changed date format
- Test formula with sample data

**Step 3**: Fix History format
If format changed:
1. Contact the policy team about StateNet
2. Update import automation to normalize format
3. Update formula regex if needed

---

## BigQuery Issues

### Issue: Cannot Access BigQuery

**Symptoms**: "Permission denied" or "Project not found"

**Diagnosis**:
1. Check if you have BigQuery access
2. Verify project ID: `guttmacher-legislative-tracker`
3. Check authentication

**Solution**:

**Step 1**: Verify project access
```bash
gcloud config get-value project
# Should return: guttmacher-legislative-tracker

gcloud projects list
# Should show the project
```

**Step 2**: Set correct project
```bash
gcloud config set project guttmacher-legislative-tracker
```

**Step 3**: Authenticate
```bash
gcloud auth application-default login
```

**Step 4**: Test access
```bash
bq ls legislative_tracker_historical
# Should list tables
```

---

### Issue: Query Returns Unexpected Results

**Symptoms**: Historical data seems incomplete or incorrect

**Common Causes**:
- Not accounting for NULL vs FALSE
- Wrong time period filter
- Methodology change not considered

**Solution**:

**Step 1**: Understand NULL patterns
```sql
-- Check if field was tracked that year
SELECT
  year,
  COUNT(*) as total_bills,
  COUNTIF(contraception IS NOT NULL) as contraception_tracked,
  COUNTIF(contraception = TRUE) as contraception_true
FROM `legislative_tracker_historical.all_historical_bills_unified`
GROUP BY year
ORDER BY year;
```

**Step 2**: Use appropriate views
- `all_historical_bills_unified`: Raw data, all years
- `comprehensive_bills_authentic`: Enhanced with helpers
- `raw_data_tracking_by_year`: Metadata about tracking

**Step 3**: Filter appropriately
```sql
-- For analyses requiring complete dates
WHERE year >= 2016  -- Introduced dates only tracked 2016+

-- For contraception analysis
WHERE year NOT BETWEEN 2006 AND 2008  -- Contraception gap

-- For modern status tracking
WHERE year >= 2006  -- Methodology revolution
```

See [Data Evolution](../historical/data-evolution.md) for methodology details.

---

## Emergency Procedures

### Emergency: Data Deletion from Airtable

**Symptoms**: Bills or other critical records deleted accidentally

**Timeline**:
- <7 days: Can restore from Airtable trash
- >7 days: Must use BigQuery backup

**Solution (<7 days)**:

**Step 1**: Stop any running automations
```
Turn OFF all automations immediately
Prevents further data modifications
```

**Step 2**: Restore from Airtable
```
Table menu → View trash
Select deleted records
Click "Restore"
```

**Step 3**: Verify restoration
- Check record counts
- Spot-check sample records
- Verify relationships intact

**Step 4**: Document incident
- What was deleted?
- How did it happen?
- How was it recovered?
- Add to INCIDENTS.md

**Solution (>7 days or Airtable restore failed)**:

**Step 1**: Use BigQuery recovery
```bash
cd bigquery
source venv/bin/activate
python etl/recovery_script.py --year 2025
```

**Step 2**: Export from BigQuery
```sql
-- Export specific year
EXPORT DATA OPTIONS(
  uri='gs://your-bucket/recovery-*.csv',
  format='CSV',
  overwrite=true
) AS
SELECT * FROM `legislative_tracker_historical.bills_2025`;
```

**Step 3**: Re-import to Airtable
- Download CSV from Google Cloud Storage
- Import to Airtable
- Verify data integrity
- Reconnect relationships

See [December 2025 Incident Report](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/INCIDENTS.md) for detailed recovery example.

---

### Emergency: Website Export Corrupted Public Data

**Symptoms**: Website Exports table empty or contains bad data

**Impact**: PUBLIC WEBSITE AFFECTED

**Immediate Actions**:

**Step 1**: Assess damage
```
Check Website Exports table
Is it empty? Partially populated? Bad data?
```

**Step 2**: Contact web team
- Advise NOT to pull latest export
- Website may still have previous data

**Step 3**: Restore Website Exports
Option A: Re-run export script
```
If Bills table intact:
Run website-export script
Verify quality score >95%
Provide to web team
```

Option B: Use previous export
```
If have backup CSV:
Import backup to temp table
Verify with policy team
Provide to web team
```

**Step 4**: Verify website
- Check public tracker website
- Verify data displays correctly
- Spot-check sample bills

**Step 5**: Post-mortem
- What caused corruption?
- Update deployment guide
- Add safeguards to prevent recurrence

---

## Getting Help

### Issue Not Listed Here?

**Step 1**: Check existing documentation
- [Airtable User Manual](../user-guides/airtable-user-manual.md)
- [Deployment Guide](deployment-guide.md)
- [BigQuery Migration Report](../historical/bigquery-migration.md)

**Step 2**: Search GitHub issues
- May be known issue with solution
- Create new issue if novel problem

**Step 3**: Contact appropriate team member

**For technical/script issues**:
- Contact the technical team

**For policy/categorization questions**:
- Contact the policy team

**For legal review questions**:
- Contact the legal team

**For website/IT issues**:
- Contact the web/IT team

### Creating a Good Bug Report

Include:
1. **What you were trying to do**
2. **What you expected to happen**
3. **What actually happened**
4. **Error messages** (exact text)
5. **Steps to reproduce**
6. **Screenshots** if helpful
7. **When it started** (worked before?)

---

**Last Updated**: Auto-updated via git-revision-date plugin
