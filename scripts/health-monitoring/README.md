# Policy Tracker Health Monitor

## Overview

This script provides an automated health monitoring system for legislative policy tracking in Airtable. It analyzes your database and generates comprehensive reports on data quality, bill status distribution, and potential issues requiring attention.

## Features

- **Weekly Health Checks**: Evaluates your database and generates a detailed report
- **Quality Scoring**: Calculates an overall quality score based on completeness and accuracy
- **Bill Status Breakdown**: Shows distribution of bills across legislative statuses
- **Category & Intent Analysis**: Tracks policy categories and intent classifications 
- **Issue Detection**: Identifies data problems like inconsistent dates and duplicate bills
- **Actionable Recommendations**: Provides specific suggestions for improvement

## Requirements

- Airtable base with the following tables:
  - Bills
  - StateNet Raw Import 
  - System Monitor
  - Website Exports

## Setup

### 1. Create the System Monitor Table

Create a new table called "System Monitor" with these fields:

| Field Name | Type | Description |
|------------|------|-------------|
| Check Date | DateTime | When the check was performed |
| Check Type | Single select (Weekly/Post-Import/Manual) | What triggered this check |
| Related Import | Text | Import batch ID (if applicable) |
| Days Since Last Check | Number | Days since previous health check |
| Bills Count | Number | Total bills being tracked |
| Bills by Status | Long Text | Breakdown of bills by status |
| Bills Missing Info | Number | Bills with required fields missing |
| Bills Missing Categories | Number | Bills without category assignment |
| Bills Missing Blurbs | Number | Bills needing blurbs but missing them |
| Recently Modified | Number | Bills changed since last check |
| Last Export Date | DateTime | When website export was performed |
| Export Count | Number | Number of bills in last export |
| New Bills Since Last Check | Number | Bills added since previous check |
| Active States | Text | States with active bills |
| All States | Text | All states in the database |
| Categories Coverage | Text | Categories in use |
| Status Changes Since Last Check | Number | Bills with status changes |
| Intent Breakdown | Text | Bills by intent type |
| High Priority Items | Number | Enacted/Vetoed bills needing attention |
| Potential Issues | Long Text | Detected database issues |
| Quality Score | Number | Overall data quality (0-100) |
| Detailed Report | Long Text | Complete health check report |

### 2. Configure Automation

1. Create a new automation in Airtable
2. Set the trigger to run weekly (e.g., Monday morning)
3. Add a "Run script" action
4. Paste the entire script code
5. Test the automation
6. Enable the automation

## Configuration Options

The script configuration is in the `CONFIG` object at the top:

```javascript
const CONFIG = {
    TABLES: {
        BILLS: 'Bills',                     // Your bills table name
        RAW_STATENET: 'StateNet Raw Import', // Your import table name
        SYSTEM_MONITOR: 'System Monitor',   // System monitor table name
        WEBSITE_EXPORTS: 'Website Exports'  // Exports table name
    },
    BILLS_FIELDS: {
        // Field names in your Bills table
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        STATUS: 'Current Bill Status',
        PRIMARY_TOPICS: 'Policy Categories',
        INTENT: 'Intent',
        LAST_ACTION: 'Last Action',
        LAST_MODIFIED: 'Last Updated',
        WEBSITE_BLURB: 'Website Blurb',
        INTRODUCED_DATE: 'Introduction Date',
        SPECIFIC_POLICIES: 'Specific Policies'
    },
    // Statuses considered "active"
    ACTIVE_STATUSES: [
        'Introduced', 
        'In First Chamber', 
        'Passed First Chamber',
        'In Second Chamber',
        'Passed Both Chambers',
        'On Governor\'s Desk'
    ],
    // Statuses that should have website blurbs
    NEEDS_BLURB_STATUSES: [
        'Enacted',
        'Vetoed',
        'Passed Both Chambers',
        'On Governor\'s Desk'
    ]
};
```

Adjust the field names and values to match your Airtable structure.

## Understanding the Results

### Quality Score

The quality score (0-100) is calculated based on:

- **Required Fields** (30%): Percentage of bills with all required fields
- **Category Assignment** (30%): Percentage of bills with categories assigned
- **Website Blurbs** (40%): Percentage of bills that need blurbs and have them

### High Priority Items

Bills that need immediate attention, specifically:

- Enacted or Vetoed bills without website blurbs

### Potential Issues

Data problems detected during the check, such as:

- Status/date inconsistencies (e.g., Enacted status but no Enacted Date)
- Duplicate bill IDs

## Troubleshooting

If the script encounters errors:

1. **Field Name Issues**: Check that all field names in CONFIG match your Airtable exactly
2. **Missing Tables**: Verify all required tables exist
3. **Field Type Mismatches**: Ensure fields are the expected type (single/multiple select, text, etc.)
4. **Script Timeout**: For very large databases, try optimizing queries or running at off-peak times