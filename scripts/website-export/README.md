# Website Export Script

## 🌐 Overview

The Website Export Script transforms internal legislative tracking data into a public-facing format suitable for the Guttmacher Institute's website. This critical integration ensures accurate, timely information reaches the public while maintaining data integrity through comprehensive validation and transformation processes.

### Key Capabilities

- **Complete Data Refresh**: Implements clean slate approach for consistency
- **Smart Field Mapping**: Transforms complex internal data to web-friendly format
- **Subpolicy Extraction**: Handles up to 10 subpolicies per bill with filtering
- **Intent Flag Generation**: Creates binary indicators from multi-select fields
- **Rich Text Handling**: Properly extracts content from formatted fields
- **Duplicate Detection**: Identifies and removes duplicate bills
- **Validation & Reporting**: Comprehensive error checking with detailed summaries

## 🔄 Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Bills Table   │────▶│ Website Export   │────▶│ Website Exports │
│ (Source Data)   │     │     Script       │     │     Table       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         │                       ▼                         ▼
         │              ┌──────────────────┐      ┌─────────────────┐
         │              │   Validation &   │      │   CSV Export    │
         └─────────────▶│   Transformation │      │  for Website    │
                        └──────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Access to Guttmacher Policy Tracker Airtable base
- Permission to run scripts and modify tables
- Understanding of the Bills table structure

### Running the Export

1. **Navigate to Extensions**
   - Open the Policy Tracker base
   - Click "Extensions" in the toolbar
   - Select "Website Exports v2"

2. **Review Pre-run Checklist**
   - [ ] Recent data import completed
   - [ ] Health check shows good quality score
   - [ ] No ongoing bill updates
   - [ ] Previous export archived if needed

3. **Execute Script**
   - Click "Run" button
   - Monitor progress in console
   - Review summary report
   - Check for any errors

4. **Export Results**
   - Go to Website Exports table
   - Use "Download CSV" option
   - Send to web team

## ⚙️ Configuration

The script configuration controls field mappings and filtering:

```javascript
const CONFIG = {
    // Source field mappings from Bills table
    FIELDS: {
        // Identifiers
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        
        // Status and intent
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent',
        ACTION_TYPE: 'Action Type',
        
        // Policy categorization
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies',
        
        // Content
        WEBSITE_BLURB: 'Website Blurb',
        
        // Key dates
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        
        // Validation
        DATE_VALIDATION: 'Date Validation'
    },
    
    // Legacy subpolicies to filter out
    UNSUPPORTED_SUBPOLICIES: [
        "AB Misc Neutral",
        "AB Ban Partial-Birth Abortion",
        "CPC Misc Restrictive",
        "FP Funding Restricted Other",
        "FP Right to Contraception",
        "INS Misc Positive",
        "Pregnancy HIV Test for Preg Women",
        "Parental Leave",
        "Repeals Ban All or Most AB Ban",
        "Repeals Counsel Perinatal Hospice Info",
        "Sex Ed Misc Neutral",
        "Sex Ed Misc Positive",
        "Sex Ed Misc Restrictive",
        "STI Misc Positive",
        "STI Misc Restrictive",
        "Sed Ed STI Neutral",
        "Repeals Ban on D and E Method"
    ]
};
```

## 📊 Field Mapping Reference

### Input Fields (Bills Table) → Output Fields (Website Exports)

| Source Field | Output Field | Transformation |
|-------------|--------------|----------------|
| State | State | Direct copy |
| BillType | BillType | Direct copy |
| BillNumber | BillNumber | Convert to string |
| Action Type | Ballot Initiative | Binary: 1 if includes "Ballot Initiative", else 0 |
| Action Type | Court Case | Binary: 1 if includes "Court Case", else 0 |
| Specific Policies | Subpolicy1-10 | First 10 policies, filtered for unsupported |
| Website Blurb | WebsiteBlurb | Rich text extraction, newline removal |
| Last Action | Last Action Date | Date formatting (YYYY-MM-DD) |
| Introduction Date | IntroducedDate | Date formatting |
| Passed 1 Chamber Date | Passed1ChamberDate | Date formatting |
| Passed Legislature Date | PassedLegislature | Date formatting |
| Passed Legislature Date | Passed 2 Chamber | Binary: 1 if date exists, else 0 |
| Vetoed Date | VetoedDate | Date formatting |
| Vetoed Date | Vetoed | Binary: 1 if date exists, else 0 |
| Enacted Date | EnactedDate | Date formatting |
| Enacted Date | Enacted | Binary: 1 if date exists, else 0 |
| Intent | Positive | Binary: 1 if includes "Positive", else 0 |
| Intent | Neutral | Binary: 1 if includes "Neutral", else 0 |
| Intent | Restrictive | Binary: 1 if includes "Restrictive", else 0 |

## 📋 Export Process Details

### 1. Data Cleanup Phase
```javascript
// Script clears all existing records
const existingRecords = await exportTable.selectRecordsAsync();
for (let i = 0; i < recordIds.length; i += 50) {
    const batchIds = recordIds.slice(i, i + 50);
    await exportTable.deleteRecordsAsync(batchIds);
}
```

### 2. Transformation Phase
- Loads all bills (no filtering)
- Validates required fields
- Transforms each record
- Handles rich text fields
- Applies date formatting
- Filters unsupported subpolicies

### 3. Validation Phase
- Checks for future dates
- Identifies missing required fields
- Detects duplicate bills
- Logs all issues

### 4. Export Creation Phase
- Creates records in batches of 50
- Maintains transformation audit trail
- Generates comprehensive summary

## 🔍 Export Summary Sections

The script generates a detailed summary report:

### Statistics Section
```
📊 Statistics
- Total records processed: 3,456
- Successfully exported: 3,421
- Errors encountered: 35
- Records with empty Website Blurb: 234 (7%)
```

### Intent Breakdown
```
📑 Intent Breakdown
- Restrictive: 1,890
- Positive: 1,234
- Neutral: 297
```

### State Distribution
```
🌎 State Breakdown
- TX: 456
- CA: 389
- NY: 234
[... all states listed]
```

### Data Quality Issues
```
⏰ Date Validation Issues
15 bills were skipped due to future dates:

- TX-HB123: 🚫 Enacted Date (2025-12-31) is in the future
- CA-SB456: 🚫 Vetoed Date (2025-06-15) is in the future
```

## 🐛 Troubleshooting

### Common Issues

#### Website Blurbs Not Exporting
**Problem**: ~40% of blurbs showing as null  
**Solution**: Script now handles rich text fields properly
```javascript
// Rich text field handling
if (typeof websiteBlurbValue === 'object' && websiteBlurbValue !== null) {
    websiteBlurb = websiteBlurbValue.text || '';
}
```

#### Duplicate Bills in Export
**Problem**: Same bill appears multiple times  
**Solution**: Script includes duplicate detection
```javascript
// Duplicate checking implemented
const duplicates = checkForDuplicates(exportRecords);
// First occurrence kept, subsequent removed
```

#### Script Timeout
**Problem**: Export fails on large datasets  
**Solutions**:
- Run during off-peak hours
- Increase script timeout limit
- Contact Airtable support for enterprise limits

#### Date Format Issues
**Problem**: Dates not formatting correctly  
**Solution**: Use the formatDate function
```javascript
const formatDate = (dateValue) => {
    // Handles Date objects and strings
    // Returns YYYY-MM-DD format
    // Returns null for invalid dates
};
```

### Debug Mode

Enable detailed logging:

```javascript
// Add to top of script
const DEBUG = true;

// Throughout script
if (DEBUG) {
    console.log(`Processing bill ${billId}...`);
    console.log(`Intent values:`, intentValues);
}
```

## 📚 Best Practices

### Pre-Export Checklist

1. **Data Quality Check**
   - Run health monitor script
   - Review quality score (should be >85)
   - Address high-priority issues

2. **Timing Considerations**
   - Avoid running during active data entry
   - Schedule after import completions
   - Allow time for manual review

3. **Validation Steps**
   - Compare record counts with previous export
   - Spot-check several transformed records
   - Verify date formatting
   - Check intent flag accuracy

### Post-Export Verification

1. **Record Count Validation**
   ```sql
   -- Compare counts
   SELECT COUNT(*) FROM Bills WHERE Status != 'Dead';
   SELECT COUNT(*) FROM Website_Exports;
   ```

2. **Data Integrity Checks**
   - No null values in required fields
   - All dates in correct format
   - Subpolicies properly distributed
   - Intent flags match source data

3. **Website Team Handoff**
   - Include export summary in email
   - Note any data quality concerns
   - Provide record count comparison
   - Highlight significant changes

## 🔧 Advanced Customization

### Adding New Fields

1. **Update CONFIG**
   ```javascript
   FIELDS: {
       // ... existing fields
       NEW_FIELD: 'New Field Name'
   }
   ```

2. **Add to Transformation**
   ```javascript
   // In transformRecord function
   const newFieldValue = record.getCellValue(CONFIG.FIELDS.NEW_FIELD);
   // Apply any necessary transformation
   ```

3. **Include in Output**
   ```javascript
   return {
       // ... existing fields
       NewFieldName: transformedValue
   };
   ```

### Custom Filters

Add bill filtering logic:

```javascript
// Example: Exclude specific states
const EXCLUDED_STATES = ['AS', 'GU', 'PR'];
if (EXCLUDED_STATES.includes(state)) {
    continue; // Skip this record
}

// Example: Only export recent bills
const DAYS_THRESHOLD = 365;
const lastAction = record.getCellValue(CONFIG.FIELDS.LAST_ACTION);
if (lastAction) {
    const daysSinceAction = 
        (new Date() - new Date(lastAction)) / (1000 * 60 * 60 * 24);
    if (daysSinceAction > DAYS_THRESHOLD) {
        continue; // Skip old bills
    }
}
```

### Performance Optimization

For very large datasets:

```javascript
// 1. Selective field loading
const records = await billsTable.selectRecordsAsync({
    fields: Object.values(CONFIG.FIELDS)
});

// 2. Parallel processing
const chunks = [];
const CHUNK_SIZE = 100;
for (let i = 0; i < records.length; i += CHUNK_SIZE) {
    chunks.push(records.slice(i, i + CHUNK_SIZE));
}

// Process chunks in parallel
const results = await Promise.all(
    chunks.map(chunk => processChunk(chunk))
);
```

## 🔒 Security & Data Integrity

- **No External Calls**: Script runs entirely within Airtable
- **Audit Trail**: Each export timestamped and summarized
- **Data Validation**: Multiple checks prevent bad data export
- **Access Control**: Limited to authorized Airtable users
- **Rollback Capability**: Previous exports preserved until overwritten

## 📞 Support

**Technical Issues**: fryda.guedes@proton.me  
**Export Questions**: Contact web team  
**Script Updates**: Check this repository

## 📝 Version History

- **v2.3** (Current): Fixed rich text blurb extraction issue
- **v2.2**: Added intent value flags for website
- **v2.1**: Removed access policy mapping
- **v2.0**: Complete rewrite with validation
- **v1.0**: Initial export functionality

## 🔮 Future Enhancements

Planned improvements:
- Incremental export option
- Real-time validation warnings
- Automated quality reports
- API endpoint integration
- Historical change tracking

---

*Last updated: January 2025*