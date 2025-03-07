# Guttmacher Policy Tracker: Website Export Script

## 📝 Overview

This Airtable script automates the export of legislative bill data from the Policy Tracker to a format compatible with the external website display. It transforms bill records into a consistent format that matches the website's expected structure.

## 🌟 Key Features

- Automated export of website-ready bills 
- Proper formatting of dates and policy fields
- Extraction of subpolicies from the access database
- Mapping of intent tags (Protective, Neutral, Restrictive)
- Comprehensive export logging
- Detailed error reporting

## 🔧 Prerequisites

- Airtable base with two tables:
  1. "Bills" table - containing tracked legislation
  2. "Website Exports" table - storing export history

## 🚀 How to Use

1. **Prepare Bills for Export**:
   - Complete the "Website Blurb" field with the public-facing description
   - Check the "Ready for Website" checkbox
   - Make sure all subpolicies are properly tagged in "Specific Policies (access)"

2. **Run the Script**:
   - Navigate to the Automations or Scripts panel
   - Run the "Website Export" script
   - Review the export summary

3. **Review Exports**:
   - The script creates new records in the Website Exports table
   - Each export includes a unique batch ID for tracking
   - Lookup fields in the Bills table will automatically update

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
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies (access)',
        WEBSITE_BLURB: 'Website Blurb',
        READY_FOR_WEBSITE: 'Ready for Website',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type'
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

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Required Fields**:
   - Error will specify which fields are missing
   - Fill in all required information and try again

2. **Date Formatting Issues**:
   - Ensure date fields contain valid dates
   - Check that Last Action is properly formatted

3. **No Bills Ready for Export**:
   - Verify the "Ready for Website" checkbox is checked
   - Make sure Website Blurb is not empty

4. **SubPolicy Fields Missing**:
   - Ensure "Specific Policies (access)" field is populated
   - The script will only export the first 10 subpolicies

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

Typically this process happens bi-monthly (1st and 15th).