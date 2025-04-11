# Policy Tracker Monitoring Scripts

This repository contains scripts used for monitoring and maintaining the Guttmacher Institute's policy tracking system in Airtable.

## Health Monitor Script

### Purpose
The `policy-tracker-monitor.js` script runs a weekly health check on the policy tracking database. It counts bills, identifies issues, and generates a report on database quality.

### How to Use (this is already set up in Airtable)

1. Create a "System Monitor" table in Airtable with fields for storing metrics
2. Set up a weekly automation in Airtable that runs this script
3. Review the results in the System Monitor table each week

### Key Features

- Counts bills by status, category and intent
- Identifies bills missing website blurbs 
- Calculates quality score based on data completeness
- Finds inconsistencies like enacted bills without dates
- Stores a complete report in the System Monitor table

## Website Export Script

### Purpose

The `website-export.js` script prepares bill data for export to the public-facing website by formatting it appropriately.

### How to Use

1. Run the script by going to the extensions tab in airtable and running the "Website Exports v2" script
2. It will produce formatted records in the Website Exports table
3. Download the exports as CSV for the website team

## Where to Find These Scripts

- **In Airtable**: Open the policy tracker base, go to Automations, and view the script steps
- **In GitHub**: All scripts are stored in this repository for version control
- **Local Backups**: Backup copies are kept in the shared drive under "Policy Tracker/Scripts"

## Customizing Scripts

The most important parts to customize in the health monitor script are:

```javascript
// At the top of the file, adjust table and field names to match your Airtable
const CONFIG = {
    TABLES: {
        BILLS: 'Bills',
        RAW_STATENET: 'StateNet Raw Import',
        SYSTEM_MONITOR: 'System Monitor',
        WEBSITE_EXPORTS: 'Website Exports'
    },
    BILLS_FIELDS: {
        // Your field names here
        STATUS: 'Current Bill Status',
        PRIMARY_TOPICS: 'Policy Categories',
        // etc.
    }
};
```

## Questions?

If you have questions about these scripts or need to make changes, contact:

- Technical maintenance: <fryda.guedes@proton.me>