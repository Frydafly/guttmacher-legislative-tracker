# Website Export Script - Enhanced Version

## 🌐 Overview

The Website Export Script transforms internal legislative tracking data into a public-facing format suitable for the Guttmacher Institute's website. This enhanced version includes comprehensive quality monitoring, real-time validation, and automated reporting to ensure data integrity and perfect fidelity.

### Key Features

- **Real-time Quality Monitoring**: Comprehensive metrics tracking during export
- **100% Website Blurb Fidelity**: Ensures all existing blurbs are preserved
- **Smart Pre-flight Validation**: Identifies critical issues before export
- **Automated Quality Reports**: Detailed analytics saved to dedicated table
- **Progress Tracking**: Live progress bars and status updates
- **Enhanced Error Handling**: Detailed error reporting and debugging
- **Complete Data Refresh**: Clean slate approach for consistency
- **Duplicate Detection & Removal**: Automatic identification and handling

## 🔄 Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Bills Table   │────▶│ Enhanced Export  │────▶│ Website Exports │
│ (Source Data)   │     │     Script       │     │     Table       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         │                       ▼                         ▼
         │              ┌──────────────────┐      ┌─────────────────┐
         │              │   Quality        │      │Export Quality   │
         └─────────────▶│   Validation &   │      │Reports Table    │
                        │   Tracking       │      │                 │
                        └──────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Access to Guttmacher Policy Tracker Airtable base
- Permission to run scripts and modify tables
- **Export Quality Reports** table configured (see setup below)

### Initial Setup

Create the **Export Quality Reports** table with these fields:

| Field Name | Field Type | Settings |
|------------|------------|----------|
| Export Date | Date | Include time: ON |
| Quality Score | Number | Integer, 0-100 |
| Grade | Single Line Text | - |
| Total Records | Number | Integer |
| Success Rate | Number | Decimal, 1 place |
| Duration (seconds) | Number | Decimal, 1 place |
| Completeness Score | Number | Integer |
| Accuracy Score | Number | Integer |
| Consistency Score | Number | Integer |
| Source Blurbs | Number | Integer |
| Exported Blurbs | Number | Integer |
| Blurb Failures | Number | Integer |
| Blurb Fidelity | Number | Decimal, 1 place |
| Date Errors | Number | Integer |
| States Count | Number | Integer |
| Recommendations | Long Text | - |
| Full Report | Long Text | - |

### Running the Export

1. **Open Script Interface**
   - Navigate to the Policy Tracker base
   - Go to Extensions → Scripts
   - Open the Website Export script

2. **Pre-flight Validation**
   - Script automatically runs validation checks
   - Reviews data quality issues
   - Flags critical problems
   - Shows warnings and info items

3. **Execute Export**
   - Click through validation prompts
   - Monitor real-time progress
   - Watch quality metrics
   - Review comprehensive summary

4. **Export Quality Report**
   - Automatic quality report saved
   - Check Export Quality Reports table
   - Review grade and recommendations
   - Address any critical issues

## 📊 Quality Metrics & Scoring

### Quality Score Components

- **Completeness (30%)**: Basic field coverage + blurb fidelity
- **Accuracy (50%)**: Valid dates and data formats
- **Consistency (20%)**: No duplicate bills

### Grade Scale

- **A+ (95-100%)**: Exceptional quality
- **A (90-94%)**: Excellent quality
- **B (85-89%)**: Good quality
- **C (80-84%)**: Acceptable quality
- **D (70-79%)**: Below standard
- **F (<70%)**: Critical issues

### Critical Metrics

- **Blurb Fidelity**: Must be 100% - all existing website blurbs must export
- **Processing Failures**: Should be 0 - no data loss during transformation
- **Success Rate**: Target >95% - minimal failed transformations

## 🔍 Pre-flight Validation Checks

### Critical Issues (Require Review)
- **Duplicate Bills**: Same bill appears multiple times
- **Severely Incomplete Records**: Missing all basic identifiers

### Warnings
- **Unusual Future Dates**: Non-enacted bills with future dates (>50 bills)
- **Incomplete Records**: Missing some basic fields

### Information
- **Website Description Status**: Enacted/vetoed bills without blurbs (normal)

## 📝 Website Blurb Fidelity

The enhanced script ensures **100% fidelity** of existing website blurbs:

- **Detection**: Identifies all bills with existing website blurbs
- **Processing**: Handles rich text fields and formatting
- **Validation**: Confirms successful export of each blurb
- **Reporting**: Flags any processing failures as CRITICAL

### Blurb Processing Steps

1. **Source Detection**: Check if bill has any website blurb content
2. **Type Handling**: Process string, rich text object, or other formats
3. **Formatting**: Clean newlines, normalize spacing
4. **Validation**: Confirm non-empty result after processing
5. **Tracking**: Record success/failure for quality metrics

## ⚙️ Configuration

```javascript
const CONFIG = {
    // Source field mappings
    FIELDS: {
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        LAST_ACTION: 'Last Action',
        INTENT: 'Intent',
        SPECIFIC_POLICIES_ACCESS: 'Specific Policies',
        WEBSITE_BLURB: 'Website Blurb',
        INTRODUCED_DATE: 'Introduction Date',
        PASSED1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        VETOED_DATE: 'Vetoed Date',
        ENACTED_DATE: 'Enacted Date',
        ACTION_TYPE: 'Action Type',
        DATE_VALIDATION: 'Date Validation',
        STATUS: 'Current Bill Status',
        LAST_MODIFIED: 'Last Modified Time'
    },
    
    // Quality tracking tables
    QUALITY_REPORTS_TABLE: 'Export Quality Reports',
    
    // Legacy subpolicies filtered out
    UNSUPPORTED_SUBPOLICIES: [
        "AB Misc Neutral",
        "AB Ban Partial-Birth Abortion",
        "CPC Misc Restrictive",
        // ... complete list in script
    ],
    
    // Quality thresholds
    QUALITY_THRESHOLDS: {
        CRITICAL_SCORE: 50,
        WARNING_SCORE: 70,
        MAX_MISSING_BLURBS_PERCENT: 90,
        MAX_DATE_ERRORS: 200
    }
};
```

## 📋 Field Mapping Reference

### Input → Output Transformations

| Source Field | Output Field | Transformation |
|-------------|--------------|----------------|
| State | State | Direct copy |
| BillType | BillType | Direct copy |
| BillNumber | BillNumber | Convert to string |
| Action Type | Ballot Initiative | Binary: 1 if "Ballot Initiative", else 0 |
| Action Type | Court Case | Binary: 1 if "Court Case", else 0 |
| Specific Policies | Subpolicy1-10 | First 10, filtered for unsupported |
| Website Blurb | WebsiteBlurb | Rich text extraction, 100% fidelity |
| Intent | Positive/Neutral/Restrictive | Binary flags |
| Date fields | Formatted dates | YYYY-MM-DD format |

## 🔍 Export Summary Sections

### Quality Score Banner
```
🏆 Quality Score: 92/100 (A)

Score Components:
- Completeness: 89% - Data field coverage
- Accuracy: 95% - Valid dates and formats  
- Consistency: 100% - No duplicates
```

### Website Blurb Fidelity
```
📝 Website Blurb Fidelity
- Bills with Source Blurbs: 234
- Successfully Exported: 234
- Processing Failures: 0
- Fidelity Rate: 100.0%
✅ Perfect fidelity: All existing blurbs exported successfully
```

### Export Statistics
```
📈 Export Statistics
- Total Processed: 3,456
- Successfully Exported: 3,421
- Failed: 35
- Success Rate: 99.0%
- Processing Time: 45.3 seconds
```

### Coverage Analysis
```
🗺️ Coverage Analysis
- States Represented: 48/50
- Unique Policies: 127
- Intent Distribution:
  - Positive: 1,234
  - Neutral: 297
  - Restrictive: 1,890
  - No Intent: 35
```

## 🐛 Troubleshooting

### Enhanced Error Messages

The script provides detailed error information:

```
❌ Could not save quality report:
   Error: Field 'Blurb Fidelity' cannot accept this value
   Make sure the 'Export Quality Reports' table exists with correct field structure

📋 Required table structure:
   Table name: "Export Quality Reports"
   Fields needed: Export Date (Date), Quality Score (Number), Grade (Text), etc.
   See README.md for complete field specifications
```

### Common Issues

#### Quality Report Not Saving
- **Problem**: Records not appearing in Export Quality Reports table
- **Solution**: Verify table exists with exact field names and types
- **Check**: Field types must match (Number vs Text vs Date)

#### Website Blurbs Missing
- **Problem**: Some blurbs not exporting despite existing in source
- **Solution**: Check Blurb Fidelity metrics in quality report
- **Debug**: Review Full Report JSON for processing details

#### Low Quality Score
- **Problem**: Score below acceptable threshold
- **Solution**: Review recommendations in quality report
- **Action**: Address high-priority issues before public export

### Debug Mode

Enable detailed logging:

```javascript
// Add detailed console output
console.log('Blurb processing:', {
    hasSource: hasSourceBlurb,
    hasExported: hasExportedBlurb,
    sourceType: typeof websiteBlurbValue,
    finalLength: websiteBlurb.length
});
```

## 📚 Best Practices

### Pre-Export Checklist

1. **Data Quality Validation**
   - Run health monitoring script first
   - Address any critical issues
   - Verify recent data imports completed

2. **Table Structure Verification**
   - Confirm Export Quality Reports table exists
   - Check all required fields configured correctly
   - Test with small dataset if uncertain

3. **Timing Considerations**
   - Avoid during active data entry periods
   - Allow sufficient time for full processing
   - Schedule during off-peak hours for large exports

### Post-Export Verification

1. **Quality Report Review**
   - Check overall quality score and grade
   - Review blurb fidelity (must be 100%)
   - Address any HIGH or CRITICAL recommendations

2. **Record Count Validation**
   - Compare with previous export counts
   - Verify expected number of new/changed bills
   - Investigate significant discrepancies

3. **Spot Check Validation**
   - Manually verify several transformed records
   - Check website blurb preservation
   - Confirm date formatting accuracy
   - Validate intent flag logic

## 🔧 Advanced Features

### Quality Thresholds Customization

Adjust scoring sensitivity:

```javascript
QUALITY_THRESHOLDS: {
    CRITICAL_SCORE: 60,        // Raise for stricter requirements
    WARNING_SCORE: 80,         // Adjust warning level
    MAX_DATE_ERRORS: 100       // Lower tolerance for date issues
}
```

### Custom Validation Rules

Add business-specific validation:

```javascript
// Example: Validate enacted bills have blurbs
if (status === 'Enacted' && !websiteBlurb) {
    metrics.addWarning({
        type: 'Missing Critical Blurb',
        bill: billId,
        message: 'Enacted bill missing website description'
    });
}
```

### Progress Tracking Customization

Modify update frequency:

```javascript
// More frequent updates for detailed tracking
const updateInterval = Math.max(1, Math.floor(total / 50)); // 2% increments

// Or time-based updates
if (Date.now() - lastUpdate > 500) { // Update every 500ms
    // Show progress
}
```

## 🔒 Data Integrity & Security

- **100% Fidelity Guarantee**: All existing content preserved
- **Comprehensive Validation**: Multiple quality checks prevent bad exports
- **Audit Trail**: Detailed quality reports for every export
- **Error Recovery**: Clear error messages for quick resolution
- **No Data Loss**: Failed records logged, not silently dropped

## 📞 Support & Maintenance

**Technical Issues**: <fryda.guedes@proton.me>  
**Quality Questions**: Review Export Quality Reports table  
**Script Updates**: Check this repository for latest version

## 📝 Version History

- **v3.0** (Current): Enhanced version with quality monitoring, blurb fidelity tracking, and automated reporting
- **v2.3**: Fixed rich text blurb extraction issue  
- **v2.2**: Added intent value flags for website
- **v2.1**: Removed access policy mapping
- **v2.0**: Complete rewrite with validation
- **v1.0**: Initial export functionality

---

*Enhanced Website Export Script - Ensuring Data Quality and Integrity*  
*Last updated: January 2025*