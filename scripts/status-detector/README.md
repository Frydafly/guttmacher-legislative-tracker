# Status Change Detector

This script automates the detection of significant changes in bill status and history that require review.

## Setup

1. Copy the entire contents of `index.js`
2. Create a new Airtable automation
3. Add a "Run script" action
4. Paste the script
5. Set up the trigger (recommended: hourly or daily)

## Configuration

The script uses two main configuration objects:

### Status Config
```javascript
STATUS_CONFIG = {
    CRITICAL_CHANGES: ['Enacted', 'Vetoed', 'Dead'],
    REVIEW_CHANGES: ['Passed First Chamber', ...],
    SIGNIFICANT_ACTIONS: ['amended', 'substituted', ...]
}
```

### Field Names
```javascript
FIELDS = {
    BILL_ID: 'BillID',
    STATE: 'State',
    // etc.
}
```

## Output

The script generates a markdown-formatted report with three sections:
1. Critical Updates Needed 🚨
2. Significant Actions 📝
3. Review Needed 👀

## Example Output
```
**Status Change Detection Summary**

🚨 **Critical Updates Needed**
- NY S1234 (Enacted): Needs website update

📝 **Significant Actions**
- CA AB5678: 03/28/2024 Signed by governor. Chapter 314.

👀 **Review Needed**
- TX HB910 (Passed First Chamber): Chamber movement detected
```
