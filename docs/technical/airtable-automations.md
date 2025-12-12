# Airtable Automations

This document describes the automated scripts that run within the Airtable base to maintain data quality, generate reports, and export data.

## Overview

All automation scripts are stored in the [`airtable-scripts/`](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts) directory of this repository. These scripts run inside Airtable's automation platform using JavaScript.

!!! important "Environment Constraints"
    Airtable scripts run in a sandboxed environment with:

    - No external npm packages
    - No require() or import statements
    - Access only to Airtable's built-in objects: `base`, `table`, `output`, `input`
    - 30-second execution timeout limit

## Active Automations

### Health Monitoring Script

**Location**: [airtable-scripts/health-monitoring/](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/health-monitoring)

**Purpose**: Weekly automated health checks that calculate data quality scores and identify issues

**Schedule**: Every Monday at 6:00 AM

**What it does**:
- Counts total bills and breaks down by status
- Identifies bills with missing information (blurbs, categories, dates)
- Calculates overall quality score (0-100)
- Flags high-priority items needing attention
- Records results in System Monitor table

**Key metrics tracked**:
- Bills count by status (Introduced, Enacted, Vetoed, etc.)
- Missing website blurbs
- Missing policy categories
- Data completeness percentage
- Quality score trending

**Output**: Creates a record in the System Monitor table with timestamp and metrics

**→ [Full Documentation](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/airtable-scripts/health-monitoring/README.md)**

---

### Partner Email Report Script

**Location**: [airtable-scripts/partner-email-report/](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/partner-email-report)

**Purpose**: Bi-weekly report generator that creates HTML/text emails about recent legislative activity

**Schedule**: 1st and 15th of each month at 8:00 AM

**What it does**:
- Filters bills enacted or vetoed in the last 14 days
- Groups by state and policy category
- Generates both HTML and plain text versions
- Includes bill summaries with links
- Sends via Airtable's email action

**Report sections**:
1. **Summary**: High-level statistics
2. **Enacted Bills**: By state, with blurbs
3. **Vetoed Bills**: By state, with blurbs
4. **Methodology**: Brief explanation of categorization

**Recipients**: Configured in Airtable automation settings

**→ [Full Documentation](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/airtable-scripts/partner-email-report/README.md)**

---

### Website Export Script

**Location**: [airtable-scripts/website-export/](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/website-export)

**Purpose**: Manual export script that transforms bill data for public website consumption

**Trigger**: Manual run by policy team (not scheduled)

**What it does**:
- Clears existing Website Exports table
- Validates Bills table data quality
- Transforms bills into website format
- Maps multi-select fields to individual columns
- Converts intent flags (Protective, Neutral, Restrictive)
- Exports as CSV for website team

**Pre-flight validation**:
- Checks for required fields
- Validates date formats
- Ensures BillID uniqueness
- Calculates quality score (warns if <95%)

**Export format**:
- One row per bill
- Flattened structure (no nested data)
- Date fields as YYYY-MM-DD
- Binary flags (1/0) for intent
- Up to 10 subpolicy columns

**Quality reporting**: Creates record in Export Quality Reports table with metrics

**→ [Full Documentation](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/airtable-scripts/website-export/README.md)**

---

### Supersedes Detector Script

**Location**: [airtable-scripts/supersedes-detector/](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/supersedes-detector)

**Purpose**: Detects when regulations supersede or are superseded by other regulations

**Trigger**: Manual run or scheduled (varies by need)

**What it does**:
- Analyzes History field text for supersede patterns
- Extracts regulation numbers
- Creates linkages in Regulations table
- Updates Supersedes and Superseded By fields

**Pattern detection**:
- "supersedes [regulation number]"
- "superseded by [regulation number]"
- Various date and citation formats

**Use case**: Tracking regulatory changes over time, especially for emergency rules

**→ [Full Documentation](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/airtable-scripts/supersedes-detector/README.md)**

---

## StateNet Import Processor

**Note**: This automation is configured directly in Airtable (not version-controlled in this repo)

**Trigger**: When new record created in StateNet Raw Import table

**What it does**:
- Matches StateNet Bill ID to existing Bills
- Creates new Bills record if no match found
- Updates existing Bills record if match found
- Preserves manual categorization work
- Links StateNet import to Bills record

**Logic**:
1. Check if BillID already exists in Bills table
2. If exists: Update fields that changed (preserve manual work)
3. If new: Create Bills record with data from StateNet
4. Link StateNet Raw Import record to Bills record
5. Mark as "Needs Review" for policy team

---

## Deployment Process

All scripts follow the same deployment process:

1. **Edit**: Modify script in this repository
2. **Test**: Run locally or in test Airtable base
3. **Commit**: Push changes to GitHub with clear message
4. **Deploy**: Copy from GitHub into Airtable automation
5. **Monitor**: Check first few runs for errors

**→ [Deployment Guide](deployment-guide.md)** for detailed steps

---

## Script Configuration

Each script has a `CONFIG` object at the top mapping Airtable field names:

```javascript
const CONFIG = {
  BILLS_TABLE: 'Bills',
  STATE_FIELD: 'State',
  STATUS_FIELD: 'Current Bill Status',
  // ... more field mappings
};
```

!!! warning "Field Name Changes"
    If you rename fields in Airtable, you **must** update the CONFIG object in each affected script, or the automation will fail.

---

## Troubleshooting Automations

**Common issues**:

| Issue | Solution |
|-------|----------|
| Script timeout | Reduce batch size or add pagination |
| Field not found | Check CONFIG object field names |
| Permission denied | Verify automation has base access |
| Unexpected results | Check console.log output in run history |

**→ [Runbook](runbook.md#script-failures)** for detailed troubleshooting

---

## Monitoring & Logs

**Where to check**:
1. **Airtable UI**: Automations tab → Find automation → Run history
2. **System Monitor table**: Weekly health check results
3. **Export Quality Reports table**: Website export metrics

**What to monitor**:
- Automation run success/failure rate
- Data quality scores trending down
- Export quality scores below 95%
- Script execution time approaching 30s limit

---

## Adding New Automations

When creating new automations:

1. **Create directory** in `airtable-scripts/[automation-name]/`
2. **Add script file**: `[automation-name].js`
3. **Create README**: Document purpose, schedule, dependencies
4. **Test thoroughly**: Use "Test run" in Airtable
5. **Update this page**: Add to Active Automations section above
6. **Deploy**: Follow deployment guide

**→ [Deployment Guide](deployment-guide.md)** for full process

---

## Source Code

All automation scripts are open source and version-controlled:

**GitHub Repository**: [airtable-scripts/](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts)

Each script directory contains:
- `.js` file - The script code
- `README.md` - Documentation
- Example screenshots (if applicable)

---

## Questions?

- **Script errors**: See [Runbook](runbook.md)
- **Deployment help**: See [Deployment Guide](deployment-guide.md)
- **Technical issues**: Contact the technical team
