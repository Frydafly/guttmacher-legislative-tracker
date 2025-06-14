# Website Export Script - Critical Test Checklist

## 🚨 CRITICAL: Run these tests before deploying any changes

This checklist ensures critical functionality remains intact. Any failure = DO NOT DEPLOY.

---

## 1. ✅ Pre-flight Validation Tests

### Test 1.1: Date Validation Field Check
**CRITICAL**: The script MUST use the Date Validation field emoji, not calculate dates itself
- [ ] Verify script checks `FIND('🚫', {Date Validation}) > 0`
- [ ] Confirm ANY record with 🚫 emoji in Date Validation = CRITICAL error
- [ ] Ensure NO date calculations in the script
- [ ] Test with a bill that has 🚫 emoji - should block export

### Test 1.2: Duplicate BillID Detection  
**CRITICAL**: Must use BillID as unique identifier
- [ ] Verify duplicate check uses `record.getCellValue(CONFIG.FIELDS.BILL_ID)`
- [ ] Confirm duplicates are detected in Bills table, NOT Website Exports
- [ ] Test with duplicate BillIDs - should show critical error
- [ ] Ensure BillID is NOT included in export records

### Test 1.3: Missing Required Fields Display
**CRITICAL**: Must show smart summary instead of overwhelming lists
- [ ] Verify missing fields show compact summary tables
- [ ] Confirm ≤20 bills: shows all specific bills to fix
- [ ] Confirm >20 bills: shows only critical ones (e.g., missing BillType)
- [ ] Test that non-critical missing field patterns are summarized, not listed

---

## 2. 📝 Website Blurb Fidelity Tests

### Test 2.1: 100% Blurb Export
**CRITICAL**: ALL existing blurbs MUST export
- [ ] Create test bill with website blurb
- [ ] Run export
- [ ] Verify blurb appears in Website Exports table
- [ ] Check Quality Report shows 100% blurb fidelity

### Test 2.2: Rich Text Handling
- [ ] Test with plain text blurb
- [ ] Test with rich text formatted blurb
- [ ] Test with blurb containing special characters
- [ ] Verify all export correctly

---

## 3. 💾 Export Success Tests

### Test 3.1: Quality Report Only on Success
**CRITICAL**: Quality report MUST NOT save if export fails
- [ ] Force an export failure (e.g., wrong field name)
- [ ] Verify NO quality report created
- [ ] Verify error message shows "Export failed - no quality report will be saved"
- [ ] Fix issue and verify quality report saves on success

### Test 3.2: Field Mapping Accuracy
**CRITICAL**: No BillID in export
- [ ] Verify export record does NOT contain BillID field
- [ ] Confirm all other fields map correctly:
  - State, BillType, BillNumber
  - All 10 Subpolicy fields
  - All date fields
  - Intent flags (Positive/Neutral/Restrictive)

---

## 4. 🔍 Quality Threshold Tests

### Test 4.1: Date Error Tolerance = 0
**CRITICAL**: ANY date error must be flagged
- [ ] Verify MAX_DATE_ERRORS = 0 in config
- [ ] Test with 1 🚫 emoji in Date Validation - should show critical error
- [ ] Confirm no "tolerance" for date issues

### Test 4.2: No Blurb Requirements
- [ ] Verify NO quality penalties for missing blurbs
- [ ] Export with 0 blurbs should still get good score
- [ ] Only track blurb FIDELITY (existing ones must export)

---

## 5. 🎯 Core Functionality Tests

### Test 5.1: Pre-flight Results Persistence
- [ ] Run export
- [ ] Verify pre-flight validation results stay visible
- [ ] Check for separator line "---" before export process
- [ ] Ensure validation warnings don't disappear

### Test 5.2: Error Handling
- [ ] Test with missing required fields
- [ ] Verify errors are logged with BillID
- [ ] Check failed records count in summary
- [ ] Ensure processing continues after individual failures

---

## 6. 🧪 Quick Smoke Test Procedure

Run this before ANY code changes:

1. **Backup Current Script**
   ```
   Copy entire script to website-export-backup-[date].js
   ```

2. **Test Data Setup**
   - Create test bill with:
     - 🚫 emoji in Date Validation field
     - Website blurb with "TEST BLURB CONTENT"
     - All required fields filled

3. **Run Export**
   - Should see Date Validation critical error
   - Choose "Continue Anyway"
   - Verify test bill exports with blurb

4. **Verify Results**
   - Check Website Exports for test record
   - Confirm blurb = "TEST BLURB CONTENT" 
   - Review Quality Report created
   - Delete test record

---

## 7. 🚫 DO NOT CHANGE These Critical Elements

1. **Date Validation Logic**
   - MUST use Date Validation field with 🚫 emoji check
   - NO custom date calculations
   - ANY 🚫 emoji in field = error

2. **Duplicate Detection**
   - MUST use BillID field
   - Check in Bills table only
   - Do NOT add BillID to export

3. **Blurb Processing**
   - MUST preserve ALL existing blurbs
   - Track source vs exported counts
   - 100% fidelity required

4. **Quality Report Timing**
   - ONLY save on successful export
   - Check exportSuccessful flag
   - Show appropriate completion message

---

## 8. 📊 Expected Test Results

### Successful Export:
```
✅ Processing complete: X successful, Y failed
✅ Successfully created X export records
✅ Quality report saved to Export Quality Reports table
✅ Export completed successfully at [timestamp]
```

### Failed Export:
```
❌ Error creating export records: [error message]
⚠️ Export failed - no quality report will be saved
❌ Export failed at [timestamp]
```

---

## 9. 🔄 Regression Test Scenarios

### Scenario A: Date Validation Bypass Attempt
1. Try to modify date checking logic
2. **Expected**: Script should ONLY reference Date Validation field
3. **Red Flag**: Any IS_AFTER, TODAY(), or date comparison code

### Scenario B: Duplicate Logic Change
1. Try to change duplicate detection to use State-Type-Number
2. **Expected**: Must continue using BillID only
3. **Red Flag**: Concatenating fields for duplicate check

### Scenario C: Blurb Loss
1. Export 10 bills with blurbs
2. **Expected**: All 10 blurbs in Website Exports
3. **Red Flag**: Any blurb fidelity < 100%

---

## 10. 🛟 Emergency Rollback Plan

If tests fail after changes:

1. **Immediate**: Revert to backup script
2. **Investigate**: Compare changes line by line
3. **Test**: Run full checklist on backup version
4. **Document**: Note what broke and why

---

**Remember**: When in doubt, DON'T change it. The script works as-is for critical operations.

Last verified working: June 2025

## 11. 🚨 GitHub Integration Tests

### Test 11.1: Version Display
**CRITICAL**: Must show meaningful version information in reports
- [ ] Verify header shows "Enhanced with Smart Validation & GitHub Integration (June 2025)"
- [ ] Confirm GitHub repository link appears in report header
- [ ] Check footer contains all GitHub links (repository, issues, documentation)

### Test 11.2: Link Functionality
- [ ] Verify all GitHub links are clickable in Airtable output
- [ ] Test that links point to correct repository URLs
- [ ] Confirm documentation links work

---

**Remember**: The enhanced version should show meaningful version info and GitHub integration, not meaningless "v3.0"