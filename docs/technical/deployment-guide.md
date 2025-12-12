# Deployment Guide

This guide covers how to deploy and update Airtable automation scripts safely.

## Overview

Airtable scripts are **manually copied** from this GitHub repository into Airtable's automation script editor. This guide ensures you deploy correctly and can rollback if needed.

!!! warning "Important"
    Always test scripts in a development/test environment before deploying to production Airtable base.

!!! warning "Audience"
    This guide is for the **technical team** deploying script updates. Policy team members: you don't need to do this - the technical team handles script updates.

## Pre-Deployment Checklist

Before deploying any script update, complete this checklist:

- [ ] **Code reviewed**: Changes have been reviewed by technical team
- [ ] **Tested**: Script runs without errors in test environment
- [ ] **README updated**: Script's README reflects any changes
- [ ] **Changes saved**: Changes are saved to GitHub with clear description
- [ ] **Stakeholders notified**: Policy team aware of changes if user-facing
- [ ] **Backup available**: Current production script version saved

## Deployment Process

### Step 1: Get the Updated Script from GitHub

1. **Open GitHub in your browser**:
   - Go to: [github.com/Frydafly/guttmacher-legislative-tracker](https://github.com/Frydafly/guttmacher-legislative-tracker)

2. **Navigate to the script**:
   - Click on the `airtable-scripts` folder
   - Click on the script you need (e.g., `health-monitoring`)
   - Click on the `.js` file (e.g., `health-monitoring.js`)

3. **View the raw code**:
   - Click the "Raw" button (top right, next to "Blame")
   - This shows the code without GitHub formatting

4. **Copy the script**:
   - Select all: Ctrl+A (Windows) or Cmd+A (Mac)
   - Copy: Ctrl+C (Windows) or Cmd+C (Mac)

### Step 2: Backup Current Production Script

!!! danger "Critical Step - Do Not Skip"
    Always backup the current production script before making changes.

1. **Open Airtable** and navigate to:
   - Automations tab (for automation scripts)
   - Extensions tab (for extension scripts)

2. **Find the script** you're updating

3. **Save a backup copy**:
   - In Airtable, select all the code in the script editor
   - Copy it (Ctrl+C or Cmd+C)
   - Open a text editor (Notepad, TextEdit, Google Docs)
   - Paste the code
   - Save file as: `backup-health-monitoring-2025-12-12.js` (use today's date)
   - Keep this file for at least 30 days

### Step 3: Deploy to Airtable

1. **Paste new code** into Airtable script editor
   - Select all existing code
   - Paste new code from clipboard
   - Code should replace entirely

2. **Verify CONFIG object** at top of script:
   ```javascript
   const CONFIG = {
     TABLE_NAMES: {
       BILLS: 'Bills',
       EXPORTS: 'Website Exports',
       // ...
     },
     FIELD_NAMES: {
       BILL_ID: 'BillID',
       STATE: 'State',
       // ...
     }
   };
   ```

   !!! tip
       CONFIG field names must match your Airtable base exactly. If Airtable field names have changed, update CONFIG accordingly.

3. **Save the script** (Airtable auto-saves)

### Step 4: Test in Production

1. **Run the script** using Airtable's "Test" or "Run" button

2. **Monitor console output** for errors:
   - Look for `✅ Success` messages
   - Check for `❌ Error` or `⚠️ Warning` messages
   - Verify record counts match expectations

3. **Verify data changes**:
   - Check affected tables for expected updates
   - Verify no unexpected data modifications
   - Confirm automation triggered correctly (if applicable)

4. **Test edge cases** if applicable:
   - Empty data sets
   - Missing fields
   - Unusual date formats

### Step 5: Monitor for 24 Hours

After deployment, monitor for issues:

- **Day 1**: Check Airtable automation run history
- **Day 2-7**: Watch for user-reported issues
- **Week 2**: Confirm no degradation in data quality scores

## Rollback Procedure

If the script causes problems:

### Immediate Rollback

1. **Stop the automation** (if running on schedule):
   - In Airtable Automations, toggle automation OFF

2. **Restore previous version**:
   - Open your backup file from Step 2
   - Copy backup code
   - Paste into Airtable script editor
   - Save

3. **Test rollback**:
   - Run script to verify it works
   - Check that data is processing correctly

4. **Re-enable automation** (if needed)

### Investigate & Fix

1. **Review error logs** in Airtable automation history

2. **Compare old vs new**:
   - Open your backup file
   - Open the new script from GitHub
   - Look for differences between them

3. **Ask technical team to fix** the issue in GitHub

4. **Test thoroughly** before re-deploying

5. **Document the incident** in INCIDENTS.md

## Tracking Deployments

### Deployment Log

Keep a simple log of what you deployed and when:

**Create a Google Doc or spreadsheet** with these columns:

| Script Name | Date Deployed | What Changed | Deployed By |
|-------------|---------------|--------------|-------------|
| health-monitoring | 2025-12-12 | Added new quality metric | Technical team |
| website-export | 2025-12-10 | Fixed blurb validation | Technical team |

**Add a new row** each time you deploy a script update.

This helps you:
- Know what version is currently running
- Track when changes were made
- Troubleshoot if something breaks

### Version Numbering

Use semantic versioning for scripts:

- **Major** (v2.0.0): Breaking changes, major refactors
- **Minor** (v1.2.0): New features, enhancements
- **Patch** (v1.1.1): Bug fixes, small improvements

## Script-Specific Deployment Notes

### Health Monitoring Script

**Location**: `airtable-scripts/health-monitoring/`

**Frequency**: Updates ~monthly

**Special considerations**:
- Updates quality score calculations - verify scores still make sense
- Changes thresholds - confirm with policy team first
- Monitor System Monitor table after deployment

### Partner Email Report Script

**Location**: `airtable-scripts/partner-email-report/`

**Frequency**: Updates as needed (rare)

**Special considerations**:
- **DO NOT deploy mid-cycle** (between 1st-3rd or 15th-17th of month)
- Test email output format carefully
- Verify recipient list before deployment
- Coordinate with policy team if format changes

### Website Export Script

**Location**: `airtable-scripts/website-export/`

**Frequency**: Updates ~quarterly

**Special considerations**:
- **High risk** - exports to public website
- Always run pre-flight validation
- Verify quality metrics after export
- Coordinate with web team before deployment
- Never deploy on Friday (give time to catch issues)

### Supersedes Detector Script

**Location**: `airtable-scripts/supersedes-detector/`

**Frequency**: Rarely updated

**Special considerations**:
- Experimental script - check if still in use
- Low risk - only flags records, doesn't modify data

## Troubleshooting

### Common Deployment Issues

**Problem**: Script runs but produces no output

**Solution**:
- Check CONFIG object - field names may have changed in Airtable
- Verify table permissions - script may not have access
- Check filters - may be excluding all records

---

**Problem**: "Cannot read property X of undefined"

**Solution**:
- A field referenced in script doesn't exist
- Check CONFIG.FIELD_NAMES mapping
- Verify field still exists in Airtable base

---

**Problem**: Script times out

**Solution**:
- Large dataset may exceed Airtable's 30-second script limit
- Consider pagination or batch processing
- Check for infinite loops

---

**Problem**: Automation runs but doesn't trigger script

**Solution**:
- Check automation trigger conditions
- Verify automation is enabled
- Check Airtable automation run history for errors

## Best Practices

1. **Always deploy during low-usage hours** (early morning or evening)

2. **Never deploy on Fridays** - gives you weekend to catch issues

3. **Communicate changes** to policy team if user-facing

4. **Test with real data** - not just sample data

5. **Document why you made changes** in your deployment log

6. **Keep backups for 30 days** minimum

7. **Monitor for 24 hours** after deployment

---

**Questions?** See the [Runbook](runbook.md) for troubleshooting common issues.
