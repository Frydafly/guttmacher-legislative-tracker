# Enhanced Website Export Script

## 🚀 Overview

The Enhanced Website Export Script is an improved version of the standard website export that adds real-time validation, quality reporting, and comprehensive analytics. It maintains the full export approach while providing better visibility, error handling, and data quality tracking.

### Key Enhancements

- **🔍 Pre-flight Validation**: Comprehensive checks before export starts
- **📊 Real-time Progress Tracking**: Live updates during processing
- **📈 Quality Scoring**: Automated data quality assessment (0-100 score)
- **💡 Smart Recommendations**: Actionable insights based on data analysis
- **📝 Detailed Reporting**: Comprehensive summaries with metrics and analytics
- **🗄️ Quality History**: Tracks quality trends over time

## 🛠️ Setup Instructions

### Step 1: Create Required Tables

Before running the enhanced export, you need to create the following table in your Airtable base:

#### Export Quality Reports Table

This table stores quality metrics and reports from each export run.

1. **Create New Table**
   - Name: `Export Quality Reports`
   - Icon: 📊 (optional)

2. **Add Fields** (exact names required):

| Field Name | Field Type | Configuration | Description |
|------------|------------|---------------|-------------|
| `Export Date` | Date | Include time ON, Use GMT | When the export was run |
| `Quality Score` | Number | Integer, 0 decimals, Min: 0, Max: 100 | Overall quality score |
| `Grade` | Single Line Text | - | Letter grade (A+, A, B, C, D, F) |
| `Total Records` | Number | Integer, 0 decimals | Total bills processed |
| `Success Rate` | Number | Decimal, 1 decimal place | Percentage of successful exports |
| `Duration (seconds)` | Number | Decimal, 1 decimal place | How long the export took |
| `Completeness Score` | Number | Integer, 0 decimals | Data completeness component |
| `Accuracy Score` | Number | Integer, 0 decimals | Data accuracy component |
| `Consistency Score` | Number | Integer, 0 decimals | Data consistency component |
| `Missing Blurbs` | Number | Integer, 0 decimals | Count of bills missing descriptions |
| `Date Errors` | Number | Integer, 0 decimals | Count of date validation errors |
| `States Count` | Number | Integer, 0 decimals | Number of states with bills |
| `Recommendations` | Long Text | - | JSON array of recommendations |
| `Full Report` | Long Text | - | Complete JSON report |

### Step 2: Install the Script

1. **Copy Script Content**
   - Copy the entire content of `website-export-enhanced.js`

2. **Create Script in Airtable**
   - Go to Extensions → Scripting
   - Create new script named "Website Export Enhanced"
   - Paste the script content
   - Save

### Step 3: Configure Field Names (if needed)

If your field names differ from the defaults, update the CONFIG object at the top of the script:

```javascript
const CONFIG = {
    FIELDS: {
        BILL_ID: 'BillID',  // Update these to match your field names
        STATE: 'State',
        // ... etc
    }
};
```

## 📖 Usage Guide

### Running the Export

1. **Open the Script**
   - Extensions → Website Export Enhanced
   - Click "Run"

2. **Pre-flight Validation**
   - Script automatically checks for:
     - Future dates
     - Missing website blurbs
     - Duplicate bills
     - Incomplete records
   - Review the validation report
   - Choose to continue or cancel

3. **Monitor Progress**
   - Watch the real-time progress bar
   - See success/failure counts update live
   - Processing speed displayed

4. **Review Results**
   - Quality score and grade
   - Detailed statistics
   - Coverage analysis
   - Recommendations for improvement

### Understanding the Quality Score

The quality score (0-100) consists of three components:

#### Completeness (40%)
- Checks if bills have all required fields
- Tracks missing website blurbs
- Higher score = more complete data

#### Accuracy (40%)
- Validates date formats
- Checks for future dates
- Detects data format errors
- Higher score = fewer errors

#### Consistency (20%)
- Identifies duplicate bills
- Checks data relationships
- Higher score = cleaner data

### Grade Scale
- **A+ (95-100)**: Exceptional data quality
- **A (90-94)**: Excellent, minimal issues
- **B (85-89)**: Good, some improvements needed
- **C (80-84)**: Fair, several issues to address
- **D (70-79)**: Poor, significant problems
- **F (Below 70)**: Critical issues requiring immediate attention

## 📊 Output Sections

### 1. Quality Score Banner
Shows overall score, grade, and emoji indicator

### 2. Score Components
Breakdown of completeness, accuracy, and consistency scores

### 3. Export Statistics
- Total processed
- Success rate
- Processing time
- Error counts

### 4. Coverage Analysis
- States represented
- Unique policies used
- Intent distribution

### 5. Data Quality Issues
- Missing blurbs count and percentage
- Date validation errors
- Other quality concerns

### 6. Recommendations
Prioritized list of actions to improve data quality:
- **CRITICAL**: Immediate action required
- **HIGH**: Address soon
- **MEDIUM**: Plan for improvement

### 7. Error Details
First 10 errors with specific bill IDs and issues

## 🔧 Troubleshooting

### Common Issues

#### "Cannot find table 'Export Quality Reports'"
**Solution**: Create the table following Step 1 instructions exactly

#### Quality score seems low
**Check**:
- Run the standard Health Monitor first
- Review high-priority recommendations
- Focus on enacted/vetoed bills first

#### Script times out
**Solutions**:
- Run during off-peak hours
- Contact Airtable for increased limits
- Consider breaking into smaller batches

#### Validation fails repeatedly
**Actions**:
1. Address critical issues first
2. Run data cleanup scripts
3. Fix date validation errors
4. Remove duplicate bills

## 📈 Best Practices

### Before Export
1. Run Health Monitor script
2. Address any critical issues
3. Ensure no active data entry
4. Back up current export if needed

### During Export
1. Don't interrupt the process
2. Note any warnings for follow-up
3. Watch for unusual patterns

### After Export
1. Review quality report
2. Check recommendations
3. Compare score to previous exports
4. Plan improvements based on findings

## 🎯 Quality Targets

Set goals for your team:

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Overall Score | 70 | 85 | 90+ |
| Missing Blurbs | <20% | <10% | <5% |
| Date Errors | <100 | <50 | <10 |
| Success Rate | >95% | >98% | >99% |

## 📊 Using Quality Reports

The Export Quality Reports table allows you to:

1. **Track Trends**
   - Create charts showing score over time
   - Identify patterns in data quality
   - Monitor improvement efforts

2. **Compare Exports**
   - See which exports had issues
   - Track resolution of problems
   - Measure team performance

3. **Generate Insights**
   - Most common issues
   - Problematic states or policies
   - Seasonal patterns

## 🔄 Integration with Other Scripts

The enhanced export works well with:

1. **Health Monitor**: Run weekly to maintain quality
2. **Partner Email Report**: Use quality data in reports
3. **Data Cleanup Scripts**: Target issues found

## 🚨 When to Use Enhanced vs. Standard Export

### Use Enhanced Export When:
- You need quality metrics
- Troubleshooting data issues
- Monthly/quarterly reporting
- Training new team members
- After major data imports

### Use Standard Export When:
- Quick routine exports
- System resources are limited
- Quality is already verified
- Time is critical

## 📞 Support

**Technical Issues**: fryda.guedes@proton.me  
**Script Location**: `/scripts/website-export/website-export-enhanced.js`  
**Version**: 3.0

## 🔮 Future Enhancements

Planned improvements:
- Email notifications for low scores
- Automatic issue resolution suggestions
- Integration with data cleanup scripts
- Historical comparison reports
- Export scheduling

---

*Last updated: January 2025*