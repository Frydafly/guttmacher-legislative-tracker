# Partner Email Report Script

## 📧 Overview

The Partner Email Report Script generates bi-weekly legislative updates for partner organizations, providing timely information about bills affecting reproductive health and gender-affirming care policies. This automated system ensures partners stay informed about legislative developments across all U.S. states.

### Key Features

- **Bi-weekly Automated Reports**: Scheduled every two weeks for consistent updates
- **Intent-based Organization**: Bills grouped by Positive/Restrictive impact
- **Recent Activity Focus**: Highlights bills with actions in the past 14 days
- **Multi-format Output**: Generates both HTML and plain text versions
- **Smart Filtering**: Excludes dead bills and focuses on active legislation
- **State-by-State Breakdown**: Easy navigation by geographic region

## 🚀 Quick Start

### Prerequisites

- Access to Guttmacher Policy Tracker Airtable base
- Understanding of Airtable automations
- Email action configured in Airtable

### Installation Steps

1. **Copy the Script**
   ```bash
   # From this repository
   scripts/partner-email-report/partner-email-report.js
   ```

2. **Create Automation**
   - Navigate to Automations → Create automation
   - Name: "Bi-weekly Partner Email Report"

3. **Configure Trigger**
   - Type: "At scheduled time"
   - Frequency: "Every 2 weeks"
   - Day: Tuesday
   - Time: 9:00 AM ET

4. **Add Script Action**
   - Action type: "Run script"
   - Paste the script code
   - Test and verify output

5. **Add Email Action**
   - Action type: "Send email"
   - Recipients: Use output from script
   - Subject: Use output from script
   - Body: Use HTML output from script

## ⚙️ Configuration

Update the CONFIG object to match your Airtable schema:

```javascript
const CONFIG = {
    FIELDS: {
        // Bill identifiers
        BILL_ID: 'BillID',
        STATE: 'State',
        BILL_TYPE: 'BillType',
        BILL_NUMBER: 'BillNumber',
        
        // Status and intent
        STATUS: 'Current Bill Status',
        INTENT: 'Intent',
        
        // Dates and actions
        LAST_ACTION: 'Last Action',
        INTRODUCED_DATE: 'Introduction Date',
        ENACTED_DATE: 'Enacted Date',
        VETOED_DATE: 'Vetoed Date',
        PASSED_1_CHAMBER_DATE: 'Passed 1 Chamber Date',
        PASSED_LEGISLATURE_DATE: 'Passed Legislature Date',
        
        // Content
        BILL_SUMMARY: 'Bill Summary',
        WEBSITE_BLURB: 'Website Blurb'
    },
    
    // Report settings
    DAYS_TO_LOOK_BACK: 14,  // Two weeks
    
    // Email configuration
    EMAIL: {
        TO: 'partners@guttmacher.org',
        CC: 'policy-team@guttmacher.org',
        SUBJECT_PREFIX: 'Legislative Update:',
        SENDER_NAME: 'Guttmacher Policy Team'
    }
};
```

## 📊 Report Structure

### Email Header
```
Subject: Legislative Update: 45 Bills with Recent Activity (Jan 15, 2025)

Dear Partners,

Here's your bi-weekly legislative update covering bills with activity 
in the past 14 days across reproductive health and gender-affirming 
care policies.
```

### Summary Section
```
📊 Summary (Past 14 Days):
• Total bills with activity: 45
• Positive bills: 12 (27%)
• Restrictive bills: 33 (73%)
• States with activity: 23
• Enacted: 3 | Vetoed: 2 | Passed Legislature: 5
```

### Positive Bills Section
```
✅ POSITIVE BILLS (12)

CALIFORNIA
• CA AB123 - Reproductive Health Protection Act
  Status: Passed Legislature (Jan 12, 2025)
  Expands access to reproductive healthcare services and 
  protects providers from out-of-state legal actions.

• CA SB456 - Gender-Affirming Care Access
  Status: Enacted (Jan 10, 2025)
  Ensures insurance coverage for gender-affirming care and 
  prohibits discrimination.
```

### Restrictive Bills Section
```
⚠️ RESTRICTIVE BILLS (33)

TEXAS
• TX HB789 - Abortion Restriction Act
  Status: Passed 1 Chamber (Jan 14, 2025)
  Further restricts abortion access and increases penalties 
  for providers.
```

## 📋 Output Examples

### Script Outputs

The script generates four outputs for use in the email action:

1. **emailTo**: Recipient email addresses
   ```
   partners@guttmacher.org
   ```

2. **emailSubject**: Dynamic subject line
   ```
   Legislative Update: 45 Bills with Recent Activity (Jan 15, 2025)
   ```

3. **emailBodyHTML**: Formatted HTML email
   ```html
   <h2>Legislative Update</h2>
   <p>Here's your bi-weekly update...</p>
   <h3>✅ Positive Bills (12)</h3>
   <div style="margin-left: 20px;">
       <h4>CALIFORNIA</h4>
       <p><strong>CA AB123</strong> - Reproductive Health Protection Act<br>
       <em>Status: Passed Legislature (Jan 12, 2025)</em><br>
       Expands access to reproductive healthcare...</p>
   </div>
   ```

4. **emailBodyPlain**: Plain text version
   ```
   LEGISLATIVE UPDATE
   
   Here's your bi-weekly update...
   
   POSITIVE BILLS (12)
   
   CALIFORNIA
   - CA AB123 - Reproductive Health Protection Act
     Status: Passed Legislature (Jan 12, 2025)
     Expands access to reproductive healthcare...
   ```

## 🔧 Customization Options

### Adjust Reporting Period

Change the lookback window:

```javascript
// For weekly reports
CONFIG.DAYS_TO_LOOK_BACK = 7;

// For monthly reports
CONFIG.DAYS_TO_LOOK_BACK = 30;
```

### Filter by Specific States

Add state filtering:

```javascript
// Only include specific states
const TARGET_STATES = ['CA', 'NY', 'TX', 'FL'];
const filteredBills = recentBills.filter(bill => {
    const state = bill.getCellValue(CONFIG.FIELDS.STATE)?.name;
    return TARGET_STATES.includes(state);
});
```

### Add Policy Categories

Include policy category breakdown:

```javascript
// Add to CONFIG
FIELDS: {
    // ... existing fields
    POLICY_CATEGORIES: 'Policy Categories'
}

// Group by categories
const categoryCounts = {};
bills.forEach(bill => {
    const categories = bill.getCellValue(CONFIG.FIELDS.POLICY_CATEGORIES) || [];
    categories.forEach(cat => {
        categoryCounts[cat.name] = (categoryCounts[cat.name] || 0) + 1;
    });
});
```

### Custom Email Templates

Create specialized templates:

```javascript
// Executive summary template
function generateExecutiveSummary(bills) {
    const enacted = bills.filter(b => 
        b.getCellValue(CONFIG.FIELDS.STATUS)?.name === 'Enacted'
    );
    
    return `
        <div style="background: #f0f0f0; padding: 15px; margin: 20px 0;">
            <h3>🎯 Executive Summary</h3>
            <p><strong>${enacted.length} bills enacted</strong> this period</p>
            <p>Key impacts: [Analysis here]</p>
        </div>
    `;
}
```

## 🐛 Troubleshooting

### Common Issues

#### No Bills in Report
**Problem**: Email shows "No bills with recent activity"  
**Solutions**:
- Check DAYS_TO_LOOK_BACK setting
- Verify Last Action dates are being updated
- Ensure bills aren't all marked as "Dead"
- Check date field formats

#### Missing Bill Information
**Problem**: Bills appear without summaries or details  
**Solutions**:
```javascript
// Debug missing fields
console.log('Bill fields:', bill.getCellValue(CONFIG.FIELDS.BILL_SUMMARY));
console.log('Available fields:', base.getTable('Bills').fields.map(f => f.name));
```

#### Email Not Sending
**Problem**: Script runs but email doesn't send  
**Checklist**:
- [ ] Email action configured after script
- [ ] Output variables properly mapped
- [ ] Recipients field not empty
- [ ] Automation fully enabled

### Performance Optimization

For large datasets:

```javascript
// Load only necessary fields
const bills = await billsTable.selectRecordsAsync({
    fields: [
        CONFIG.FIELDS.BILL_ID,
        CONFIG.FIELDS.STATE,
        CONFIG.FIELDS.STATUS,
        CONFIG.FIELDS.INTENT,
        CONFIG.FIELDS.LAST_ACTION
    ],
    sorts: [{field: CONFIG.FIELDS.LAST_ACTION, direction: 'desc'}]
});

// Process in batches
const BATCH_SIZE = 500;
for (let i = 0; i < bills.length; i += BATCH_SIZE) {
    const batch = bills.slice(i, i + BATCH_SIZE);
    processBatch(batch);
}
```

## 📚 Best Practices

### Content Guidelines

1. **Bill Summaries**
   - Keep under 150 characters
   - Focus on key impact
   - Use clear, non-technical language

2. **Status Updates**
   - Always include date of last action
   - Highlight significant progressions
   - Note when bills are fast-tracked

3. **Intent Classification**
   - Review intent assignments regularly
   - Ensure consistency across similar bills
   - Document edge cases

### Scheduling Considerations

- **Optimal Send Times**: Tuesday/Thursday mornings
- **Avoid Holidays**: Check calendar for conflicts
- **Time Zones**: Account for recipient locations
- **Legislative Calendars**: Align with session schedules

### Quality Assurance

Before each send:
1. Review bill counts for anomalies
2. Spot-check several bills for accuracy
3. Verify all links work correctly
4. Test email rendering in multiple clients

## 🔄 Integration Options

### Webhook Integration

Send reports to external systems:

```javascript
// Add to end of script
const webhook_url = 'https://api.example.com/legislative-updates';
const payload = {
    date: new Date().toISOString(),
    bill_count: recentBills.length,
    positive_count: positiveBills.length,
    restrictive_count: restrictiveBills.length,
    states_affected: uniqueStates.length
};

// Note: Actual HTTP requests require external integration
output.set('webhookPayload', JSON.stringify(payload));
```

### Archive Reports

Store reports for historical reference:

```javascript
// Create archive record
const archiveTable = base.getTable('Email Archives');
await archiveTable.createRecordAsync({
    'Send Date': new Date(),
    'Recipients': CONFIG.EMAIL.TO,
    'Subject': emailSubject,
    'HTML Body': emailBodyHTML,
    'Plain Body': emailBodyPlain,
    'Bill Count': recentBills.length,
    'Report Type': 'Partner Bi-weekly'
});
```

## 📞 Support

**Technical Support**: fryda.guedes@proton.me  
**Partner Questions**: partners@guttmacher.org  
**Report Issues**: Create issue in this repository

## 📝 Version History

- **v2.1** (Current): Added rich text support for bill summaries
- **v2.0**: Multi-format output (HTML + plain text)
- **v1.5**: Added intent-based grouping
- **v1.0**: Initial bi-weekly report implementation

---

*Last updated: January 2025*