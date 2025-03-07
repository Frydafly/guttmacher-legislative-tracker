# Guttmacher Policy Tracker: Website Export Script

## 📝 Overview

This Airtable script automates the export of legislative bill data from the Policy Tracker to a format compatible with the external website display. It transforms bill records into a consistent format that matches the website's expected structure.

## 🌟 Key Features

- Automated export of all bills from the tracking database
- Proper formatting of dates and policy fields
- Extraction of subpolicies from the access database
- Mapping of intent tags (Protective, Neutral, Restrictive)
- Comprehensive export logging with statistics
- Detailed error reporting
- Batch processing to handle large datasets

## 🔧 Prerequisites

- Airtable base with two tables:
  1. "Bills" table - containing tracked legislation
  2. "Website Exports" table - storing export history

## 🚀 How to Use

1. **Set Up Your Airtable Base**:
   - Ensure field names match those in the CONFIG object
   - Make sure "Website Exports" table exists with required fields
   - Add "Intent (access)" and "Specific Policies (access)" fields to track policy types

2. **Run the Script**:
   - Navigate to the Automations or Scripts panel
   - Add this script as a new automation
   - Review the export summary after execution

3. **Review Exports**:
   - The script creates new records in the Website Exports table
   - Each export includes a unique batch ID for tracking
   - Export metadata and statistics are displayed in the console

## 🔍 What Gets Exported

The script maps the following fields:

### Core Bill Information

- State
- BillType
- BillNumber
- Ballot Initiative (derived from Action Type)
- Court Case (derived from Action Type)

### Content

- WebsiteBlurb
- SubPolicy1-10 (from Specific Policies (access))

### Dates

- Last Action Date
- IntroducedDate
- Passed1ChamberDate
- VetoedDate
- EnactedDate

### Intent Tags

- Positive (if Intent includes "Protective")
- Neutral (if Intent includes "Neutral")
- Restrictive (if Intent includes "Restrictive")

## ⚙️ Configuration

The script uses a CONFIG object to map fields between the Bills table and the export format:

```javascript
const CONFIG = {
    // Maps field names from the Bills table
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent (access)',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies (access)',
        WEBSITE_BLURB: 'Website Blurb',
        READY_FOR_WEBSITE: 'Ready for Website',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type'
    },

    // Maps fields in the export table
    EXPORT_FIELDS: {
        EXPORT_DATE: 'Export Date',
        EXPORT_BATCH: 'Batch ID',
        BILL_RECORD: 'Bill Record',
        EXPORTED_BY: 'Exported By'
    }
};
```

## 📊 Export Summary

Each export generates a detailed report including:

- Batch details and timestamp
- Number of successfully exported bills
- Intent breakdown (Positive/Neutral/Restrictive)
- State breakdown
- Any errors encountered

Example summary:
```

📦 Export Batch
- Batch ID: WEB_20240307_1530
- Export Date: 3/7/2025, 3:30:00 PM

📊 Statistics
- Total records processed: 125
- Successfully exported: 123
- Errors encountered: 2

📑 Intent Breakdown
- Restrictive: 62
- Positive: 45
- Neutral: 16

🌎 State Breakdown
- TX: 15
- FL: 12
- NY: 10
...
```

## 🛠️ Troubleshooting

### Common Issues

1. **Transformation Errors**:
   - The script will log specific field errors
   - Check field data types match what the script expects
   - Confirm field names match the CONFIG object

2. **Date Formatting Issues**:
   - The script attempts to normalize various date formats
   - Check for malformed dates in your source data

3. **Batch Processing Limits**:
   - The script processes records in batches of 50
   - For very large databases, the process may take some time

4. **Empty Exports**:
   - The script will continue even if no records are successfully transformed
   - Check for basic data integrity issues if no records export

### Field Naming

If you rename fields in your Airtable base, you must update the corresponding mappings in the CONFIG object to match exactly.

## 📋 Export Table Structure

The Website Exports table requires these fields:

| Field Name | Description | Type |
|------------|-------------|------|
| Batch ID | Unique export identifier | Text |
| Export Date | Timestamp of export | Date/Time |
| Bill Record | Link to source bill | Linked Record |
| Exported By | Source of export | Text |
| State | State abbreviation | Text |
| BillType | Type of bill | Text |
| BillNumber | Specific bill number | Text |
| Ballot Initiative | Flag for ballot initiatives | Text |
| Court Case | Flag for court cases | Text |
| SubPolicy1-10 | Individual policy components | Text |
| WebsiteBlurb | Website-ready description | Long Text |
| Last Action Date | Most recent date | Date |
| IntroducedDate | Introduction date | Date |
| Passed1ChamberDate | First chamber passage | Date |
| PassedLegislature | Legislature passage | Date |
| VetoedDate | Veto date | Date |
| EnactedDate | Enactment date | Date |
| Positive | Protective intent flag | Text |
| Neutral | Neutral intent flag | Text |
| Restrictive | Restrictive intent flag | Text |

## 🔄 Update Process

The full website update process involves:

1. Running this export script
2. Downloading the CSV from the Website Exports table
3. Providing the CSV to the website team
4. Website team uploads and processes the data