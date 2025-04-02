# Guttmacher Policy Tracker: Website Export Script

## 📝 Overview

This Airtable script automates the export of legislative bill data from the Policy Tracker to a format compatible with the external website display. It performs a complete refresh of the export table each time it runs, ensuring the website always has the most current data.

## 🌟 Key Features

- Complete refresh of export data (deletes old records before creating new ones)
- Proper formatting of dates and policy fields
- Extraction of subpolicies from legislative data
- Mapping of intent tags (Protective, Neutral, Restrictive)
- Conversion of legislative dates to boolean flags when needed
- Comprehensive export statistics
- Detailed error reporting

## 🔧 Prerequisites

- Airtable base with two tables:
  1. "Bills" table - containing tracked legislation
  2. "Website Exports" table - destination for formatted export data

## 🚀 How to Use

1. **Prepare Bills for Export**:
   - Complete the "Website Blurb" field with the public-facing description
   - Check the "Ready for Website" checkbox
   - Ensure all policy fields are properly categorized

2. **Run the Script**:
   - Navigate to the Automations or Scripts panel
   - Run the "Website Export" script
   - The script will clear the export table and populate it with fresh data

3. **Download Export Data**:
   - After the script completes, navigate to the Website Exports table
   - Download as CSV
   - Provide to the website team

## 🔍 What Gets Exported

The script transforms and exports the following fields:

### Core Bill Information

- State
- BillType
- BillNumber
- Ballot Initiative (derived from Action Type)
- Court Case (derived from Action Type)

### Content

- WebsiteBlurb
- Subpolicy1-10 (from Specific Policies)

### Status and Dates

- Last Action Date
- IntroducedDate
- Passed1ChamberDate
- Passed 2 Chamber (Boolean: 1/0 based on PassedLegislature date)
- PassedLegislature
- VetoedDate
- EnactedDate

### Intent Tags

- Positive (1/0 if Intent includes "Protective")
- Neutral (1/0 if Intent includes "Neutral")
- Restrictive (1/0 if Intent includes "Restrictive")

## ⚙️ Configuration

The script uses a CONFIG object to map fields. If your field names differ, update this section:

```javascript
const CONFIG = {
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
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type'
    }
};
```

## 📊 Export Summary

Each export generates a detailed report including:

- Export statistics (processed, successful, errors)
- Intent breakdown (Positive/Neutral/Restrictive)
- State breakdown
- Any errors encountered

Example summary:

```plaintext
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

1. **Field Not Found Errors**:
   - Ensure all field names in CONFIG match exactly what's in your Airtable
   - Check for typos in field names
   - Verify that all required fields exist in your tables

2. **No Records Being Exported**:
   - Confirm bills have the "Ready for Website" checkbox checked
   - Verify "Website Blurb" fields are filled out
   - Check filter conditions if customized

3. **Date Formatting Issues**:
   - The script attempts to normalize various date formats
   - Check for malformed dates in your source data

4. **Error with Batch Processing**:
   - The script processes records in batches of 50 (Airtable limit)
   - For large exports, watch for timeout errors

### Field Requirements

These fields must be properly set up in your Bills table:

- State (Single select)
- BillType (Single select)
- BillNumber (Text)
- Website Blurb (Long text)
- Ready for Website (Checkbox)
- Date fields (various)
- Intent fields (Multiple select)

## 📋 Export Table Structure

The Website Exports table should have these fields:

| Field Name | Description | Type |
|------------|-------------|------|
| State | State abbreviation | Text |
| BillType | Type of bill | Text |
| BillNumber | Specific bill number | Text |
| Ballot Initiative | Flag for ballot initiatives (1/0) | Text |
| Court Case | Flag for court cases (1/0) | Text |
| Subpolicy1-10 | Individual policy components | Text |
| WebsiteBlurb | Website-ready description | Long Text |
| Last Action Date | Most recent date | Date/Text |
| IntroducedDate | Introduction date | Date/Text |
| Passed1ChamberDate | First chamber passage | Date/Text |
| Passed 2 Chamber | Second chamber passage flag (1/0) | Text |
| PassedLegislature | Legislature passage | Date/Text |
| VetoedDate | Veto date | Date/Text |
| EnactedDate | Enactment date | Date/Text |
| Positive | Protective intent flag (1/0) | Text |
| Neutral | Neutral intent flag (1/0) | Text |
| Restrictive | Restrictive intent flag (1/0) | Text |

## 🔄 Website Update Process

The full website update process involves:

1. Running this export script
2. Downloading the CSV from the Website Exports table
3. Providing the CSV to the website team
4. Website team uploads and processes the data

Typically, this process happens bi-monthly (1st and 15th of each month).