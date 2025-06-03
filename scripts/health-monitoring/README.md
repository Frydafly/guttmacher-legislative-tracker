# Health Monitoring Script

## 📋 Overview

The Health Monitoring Script is an automated quality assurance system for the Guttmacher Legislative Tracker. It performs comprehensive weekly health checks on the policy tracking database, ensuring data integrity and identifying issues before they impact downstream systems.

### Key Capabilities

- **Automated Quality Scoring**: Generates a 0-100 score based on weighted metrics
- **Trend Analysis**: Tracks week-over-week changes and identifies anomalies
- **Issue Detection**: Finds data inconsistencies, missing fields, and validation errors
- **Smart Reporting**: Creates actionable reports with prioritized recommendations
- **Performance Monitoring**: Tracks database growth and system performance

## 🚀 Quick Start

### Prerequisites

- Administrator access to the Guttmacher Policy Tracker Airtable base
- Understanding of Airtable automations and scripting
- Access to create/modify tables and automations

### Installation Steps

1. **Copy the Script**
   ```bash
   # From this repository
   scripts/health-monitoring/health-monitoring.js
   ```

2. **Create System Monitor Table** (see detailed schema below)

3. **Set Up Automation**
   - Navigate to Automations → Create automation
   - Trigger: "At scheduled time" → Weekly → Sunday 11 PM
   - Action: "Run script" → Paste the script code

4. **Configure & Test**
   - Update CONFIG object with your field names
   - Run test to verify functionality
   - Enable automation

## 📊 System Monitor Table Schema

Create a table named "System Monitor" with these exact specifications:

### Core Metrics Fields

| Field Name | Type | Configuration | Purpose |
|-----------|------|---------------|---------|
| `Check Date` | Date | Include time, GMT | Timestamp of health check |
| `Quality Score` | Number | Integer, 0-100 | Overall database health |
| `Total Bills` | Number | Integer | Current bill count |
| `Alert Level` | Single Select | Normal, Warning, Critical | System status |

### Data Quality Fields

| Field Name | Type | Configuration | Purpose |
|-----------|------|---------------|---------|
| `Bills Missing Categories` | Number | Integer | Uncategorized bills |
| `Bills Missing Required Fields` | Number | Integer | Incomplete records |
| `Enacted Missing Blurb` | Number | Integer | Enacted without descriptions |
| `Vetoed Missing Blurb` | Number | Integer | Vetoed without descriptions |
| `Future Date Issues` | Number | Integer | Bills with future dates |

### Reporting Fields

| Field Name | Type | Configuration | Purpose |
|-----------|------|---------------|---------|
| `High Priority Items` | Long Text | Rich text ON | Critical issues list |
| `Potential Issues` | Long Text | Rich text ON | Warnings and concerns |
| `Full Report` | Long Text | Rich text ON | Complete analysis |
| `Bills by Status` | Long Text | Rich text ON | Status distribution |
| `Bills by Intent` | Long Text | Rich text ON | Intent breakdown |
| `Week Over Week Changes` | Long Text | Rich text ON | Trend analysis |

### Tracking Fields

| Field Name | Type | Configuration | Purpose |
|-----------|------|---------------|---------|
| `Bills Added This Week` | Number | Integer | New records |
| `Bills Modified This Week` | Number | Integer | Updated records |
| `Status Changes This Week` | Number | Integer | Progression tracking |
| `Processing Time` | Number | Decimal, 2 places | Script duration (seconds) |
| `Error Log` | Long Text | Rich text ON | Any errors encountered |

## ⚙️ Configuration

The script uses a configuration object that must match your Airtable schema:

```javascript
const CONFIG = {
    // Table names
    TABLES: {
        BILLS: 'Bills',                      // Main bills table
        SYSTEM_MONITOR: 'System Monitor',    // Health check results
        RAW_STATENET: 'StateNet Raw Import', // Import tracking
        WEBSITE_EXPORTS: 'Website Exports'   // Export tracking
    },
    
    // Bills table field mappings
    BILLS_FIELDS: {
        // Identifiers
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        
        // Status and categorization
        STATUS: 'Current Bill Status',
        PRIMARY_TOPICS: 'Policy Categories',
        INTENT: 'Intent',
        ACTION_TYPE: 'Action Type',
        
        // Dates
        INTRODUCED_DATE: 'Introduction Date',
        ENACTED_DATE: 'Enacted Date',
        VETOED_DATE: 'Vetoed Date',
        LAST_ACTION: 'Last Action',
        LAST_MODIFIED: 'Last Modified Time',
        
        // Content
        WEBSITE_BLURB: 'Website Blurb',
        
        // Validation
        DATE_VALIDATION: 'Date Validation'
    },
    
    // Monitoring thresholds
    THRESHOLDS: {
        CRITICAL_SCORE: 70,
        WARNING_SCORE: 85,
        MAX_MISSING_BLURBS: 50,
        MAX_UNCATEGORIZED: 100
    }
};
```

## 📈 Quality Score Calculation

The quality score provides a single metric for database health:

### Formula
```
Quality Score = (Required Fields Score × 30%) + 
                (Categorization Score × 30%) + 
                (Website Blurb Score × 40%)
```

### Score Components

1. **Required Fields (30%)**
   - Checks: State, BillType, BillNumber, Status
   - Score = (Bills with all fields / Total bills) × 100

2. **Categorization (30%)**
   - Checks: At least one policy category assigned
   - Score = (Categorized bills / Total bills) × 100

3. **Website Blurbs (40%)**
   - Checks: Enacted/Vetoed bills have descriptions
   - Score = (Bills with blurbs / Bills needing blurbs) × 100
   - Note: Executive Orders exempt from date requirements

### Score Interpretation

- **90-100**: Excellent - Minimal issues
- **80-89**: Good - Minor improvements needed
- **70-79**: Fair - Several issues to address
- **Below 70**: Critical - Immediate action required

## 📋 Report Sections Explained

### 1. Executive Summary
```
📊 Health Check Summary
━━━━━━━━━━━━━━━━━━━━━
Quality Score: 87/100 (↑ 3 from last week)
Total Bills: 3,456 (+67 from last week)
High Priority Items: 23
Status: ⚠️ Warning
```

### 2. Bill Distribution
```
📊 Bills by Status:
• Introduced: 1,234 (+45)
• In Committee: 567 (-12)
• Passed Chamber: 234 (+8)
• Enacted: 123 (+5)
• Vetoed: 45 (+2)
```

### 3. High Priority Items
Lists critical issues requiring immediate attention:
- Enacted bills missing website blurbs
- Vetoed bills without proper documentation
- Data validation errors

### 4. Trend Analysis
Week-over-week comparisons with context:
- New bills by state
- Status progression rates
- Category assignment trends

## 🔧 Customization Guide

### Adding Custom Checks

Create additional validation functions:

```javascript
// Example: Check for stale bills
function checkStaleBills(bills) {
    const STALE_DAYS = 180;
    const staleBills = [];
    
    for (const bill of bills) {
        const status = bill.getCellValue(CONFIG.BILLS_FIELDS.STATUS);
        const lastAction = bill.getCellValue(CONFIG.BILLS_FIELDS.LAST_ACTION);
        
        if (status?.name === 'In Committee' && lastAction) {
            const daysSinceAction = 
                (new Date() - new Date(lastAction)) / (1000 * 60 * 60 * 24);
            
            if (daysSinceAction > STALE_DAYS) {
                staleBills.push({
                    billId: bill.getCellValue(CONFIG.BILLS_FIELDS.BILL_ID),
                    days: Math.floor(daysSinceAction)
                });
            }
        }
    }
    
    return staleBills;
}
```

### Adjusting Scoring Weights

Modify the scoring algorithm:

```javascript
// Custom weights (must total 100)
const CUSTOM_WEIGHTS = {
    REQUIRED_FIELDS: 25,    // Reduce basic compliance weight
    CATEGORIZATION: 25,     // Equal weight for categorization
    WEBSITE_BLURBS: 35,     // Increase public content weight
    CUSTOM_METRIC: 15       // Add new metric
};
```

### Email Notifications

Add email alerts for critical issues:

```javascript
// In automation, after script action
if (output.get('alertLevel') === 'Critical') {
    // Add "Send email" action
    // To: policy-team@guttmacher.org
    // Subject: 🚨 Critical Data Quality Alert
    // Body: Use output.get('emailSummary')
}
```

## 🐛 Troubleshooting

### Common Issues

#### Script Timeout
**Problem**: Script fails with timeout error  
**Solutions**:
- Reduce batch size in queries
- Add field filters to queries
- Run during off-peak hours
- Contact Airtable for increased limits

#### Field Not Found
**Problem**: "Cannot read property 'name' of null"  
**Solutions**:
```javascript
// Debug field names
const table = base.getTable('Bills');
console.log('Available fields:', table.fields.map(f => f.name));
```

#### Quality Score Anomalies
**Problem**: Score doesn't match expectations  
**Checklist**:
- [ ] Executive Orders properly tagged in Action Type
- [ ] Date fields are Date type, not text
- [ ] Category field is multiple select
- [ ] All field mappings correct

### Performance Optimization

```javascript
// Optimize queries
const records = await table.selectRecordsAsync({
    fields: [
        CONFIG.BILLS_FIELDS.STATUS,
        CONFIG.BILLS_FIELDS.INTENT,
        CONFIG.BILLS_FIELDS.WEBSITE_BLURB
    ],
    // Add filters if needed
    filterByFormula: "NOT({Status} = 'Dead')"
});

// Use batch processing
const BATCH_SIZE = 1000;
for (let i = 0; i < records.length; i += BATCH_SIZE) {
    const batch = records.slice(i, i + BATCH_SIZE);
    // Process batch
}
```

## 📚 Best Practices

### Weekly Review Process

1. **Monday Morning**
   - Review Sunday night's health check
   - Identify critical issues
   - Assign fixes to team members

2. **Wednesday Check-in**
   - Progress on high-priority items
   - Mid-week manual health check if needed

3. **Friday Wrap-up**
   - Verify all critical issues addressed
   - Plan for next week's improvements

### Data Quality Standards

- **Required Fields**: Never leave core fields empty
- **Categorization**: Assign at least one category within 48 hours
- **Website Blurbs**: Complete within 72 hours of enactment/veto
- **Date Accuracy**: Verify all dates before entry

### Maintenance Schedule

- **Weekly**: Review health reports, fix critical issues
- **Monthly**: Analyze trends, adjust thresholds
- **Quarterly**: Update scoring weights, add new checks
- **Annually**: Major script review and optimization

## 🔒 Security Considerations

- Script runs in Airtable's sandboxed environment
- No external API calls or data exports
- Access controlled via Airtable permissions
- Audit trail maintained in System Monitor table

## 📞 Support

**Technical Issues**: fryda.guedes@proton.me  
**Airtable Support**: [Airtable Help Center](https://support.airtable.com)  
**Script Updates**: Check this repository for latest version

## 📝 Version History

- **v1.3** (Current): Added rich text field support for website blurbs
- **v1.2**: Enhanced date validation and executive order handling
- **v1.1**: Added trend analysis and performance metrics
- **v1.0**: Initial release with basic health checks

---

*Last updated: January 2025*