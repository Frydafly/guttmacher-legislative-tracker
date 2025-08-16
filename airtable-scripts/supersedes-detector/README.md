# Supersedes Relationship Detector

## 📋 Overview

The Supersedes Relationship Detector is an automated script for the Guttmacher Regulations Tracker that identifies when newer regulations potentially replace older ones. It helps maintain relationship tracking between regulations without requiring manual review of every new entry.

### Key Capabilities

- **Automatic Detection**: Identifies potential supersedes relationships when regulations are created or updated
- **Smart Matching**: Uses state, agency, and title similarity to find related regulations
- **Non-Intrusive**: Adds suggestions to Internal Notes without modifying core data
- **Efficiency**: Prevents manual cross-referencing of hundreds of regulations

## 🚀 Quick Start

### Prerequisites

- Access to the Guttmacher Regulations Tracker Airtable base
- Understanding of Airtable automations and scripting
- Permissions to create/modify automations

### Installation Steps

1. **Copy the Script**
   ```bash
   # From this repository
   airtable-scripts/supersedes-detector/supersedes-detector.js
   ```

2. **Set Up Automation**
   - Navigate to Automations → Create automation
   - Name: "Supersedes Relationship Detector"
   - Trigger: "When record is created or updated"
     - Table: Regulations
     - Fields to watch: Title, State, Issuing Agency Link
   - Action: "Run script" → Paste the script code

3. **Configure Input Variables**
   - Add input variable: `record` (Record from trigger)

4. **Test & Enable**
   - Create a test regulation record
   - Run automation test
   - Verify Internal Notes are updated
   - Enable automation

## 📊 How It Works

### Detection Algorithm

1. **Trigger**: Fires when a regulation is created or key fields are updated
2. **Filter Candidates**: Finds regulations from the same state and agency
3. **Year Check**: Only considers regulations from earlier years (potential predecessors)
4. **Title Similarity**: Extracts keywords (4+ characters) and checks for 50%+ match
5. **Report Results**: Adds findings to Internal Notes field

### Example Detection

**New Regulation**:
- Title: "Emergency Rule on Abortion Facility Licensing Requirements"
- State: "Texas"
- Agency: "Department of Health Services"
- Year: 2024

**Would Match**:
- "Abortion Facility Licensing Standards" (Texas, DHS, 2023)
- "Emergency Rules for Abortion Facility Requirements" (Texas, DHS, 2022)

**Would NOT Match**:
- "Abortion Facility Licensing" (Oklahoma, DHS, 2023) - Different state
- "Hospital Licensing Requirements" (Texas, DHS, 2023) - Low keyword match
- "Abortion Facility Licensing" (Texas, DHS, 2025) - Later year

## ⚙️ Configuration

The script uses a configuration object that must match your Airtable schema:

```javascript
const CONFIG = {
    TABLES: {
        REGULATIONS: 'Regulations'  // Main regulations table
    },
    FIELDS: {
        // Identifiers
        REG_ID: 'Reg-ID',
        STATE: 'State',
        YEAR: 'Year',
        
        // Relationships
        ISSUING_AGENCY: 'Issuing Agency',
        TITLE: 'Title',
        
        // Output
        INTERNAL_NOTES: 'Internal Notes',
        
        // Optional link fields (if using)
        SUPERSEDED_BY: 'Superseded By',
        SUPERSEDES: 'Supersedes'
    },
    
    // Matching thresholds
    THRESHOLDS: {
        MIN_KEYWORD_LENGTH: 4,      // Minimum word length to consider
        MATCH_PERCENTAGE: 0.5       // 50% of keywords must match
    }
};
```

## 📋 Field Requirements

### Required Fields

| Field Name | Type | Purpose |
|-----------|------|---------|
| `Reg-ID` | Formula | Unique identifier for each regulation |
| `State` | Single Select | State where regulation applies |
| `Year` | Number | Year of regulation |
| `Issuing Agency` | Link to Agencies | Agency that issued the regulation |
| `Title` | Single Line Text | Regulation title |
| `Internal Notes` | Long Text | Where suggestions are written |

### Optional Fields for Manual Linking

| Field Name | Type | Purpose |
|-----------|------|---------|
| `Superseded By` | Link to Regulations | Manual link to newer regulation |
| `Supersedes` | Link to Regulations (reverse) | Shows which older regulations this replaces |

## 🔧 Customization Guide

### Adjusting Match Sensitivity

```javascript
// More strict matching (fewer false positives)
const THRESHOLDS = {
    MIN_KEYWORD_LENGTH: 5,      // Longer words only
    MATCH_PERCENTAGE: 0.75      // 75% match required
};

// More lenient matching (catch more relationships)
const THRESHOLDS = {
    MIN_KEYWORD_LENGTH: 3,      // Include shorter words
    MATCH_PERCENTAGE: 0.33      // 33% match sufficient
};
```

### Adding Agency Type Filtering

```javascript
// Only match within same agency type
const candidates = query.records.filter(record => {
    return record.id !== currentRecord.id &&
           record.getCellValue("State") === currentRecord.getCellValue("State") &&
           record.getCellValue("Issuing Agency") === currentRecord.getCellValue("Issuing Agency") &&
           record.getCellValue("Agency Type") === currentRecord.getCellValue("Agency Type") && // Added
           record.getCellValue("Year") < currentRecord.getCellValue("Year");
});
```

### Enhanced Title Matching

```javascript
// Add fuzzy matching for common variations
function normalizeTitle(title) {
    return title.toLowerCase()
        .replace(/emergency rule?s?/gi, 'emergency')
        .replace(/requirements?/gi, 'requirement')
        .replace(/standards?/gi, 'standard')
        .replace(/facilities/gi, 'facility');
}
```

## 🐛 Troubleshooting

### Common Issues

#### No Matches Found for Obviously Related Regulations
**Causes**:
- Title variations too different
- Agency names don't match exactly
- Year field not populated

**Solutions**:
```javascript
// Debug: Log what's being compared
console.log('Current title keywords:', keywords);
console.log('Candidate count:', candidates.length);
candidates.forEach(c => {
    console.log('Checking:', c.getCellValue("Title"));
});
```

#### Too Many False Positives
**Causes**:
- Match threshold too low
- Common words causing matches

**Solutions**:
- Increase MATCH_PERCENTAGE to 0.6 or 0.7
- Add stopwords filter:
```javascript
const stopwords = ['rule', 'regulation', 'emergency', 'the', 'and', 'or'];
keywords = keywords.filter(word => !stopwords.includes(word));
```

#### Script Timeout
**Causes**:
- Too many regulations to check
- Complex matching logic

**Solutions**:
- Add year range limit:
```javascript
// Only check regulations from last 5 years
const fiveYearsAgo = currentRecord.getCellValue("Year") - 5;
const candidates = query.records.filter(record => {
    return record.getCellValue("Year") >= fiveYearsAgo && 
           record.getCellValue("Year") < currentRecord.getCellValue("Year");
});
```

## 📚 Best Practices

### Review Process

1. **Weekly Review**
   - Check Internal Notes for new suggestions
   - Verify and create actual links for confirmed relationships
   - Clear processed suggestions from Internal Notes

2. **Manual Override**
   - Always allow manual linking to override automation
   - Document why automatic detection might have missed relationships

3. **Continuous Improvement**
   - Track false positives/negatives
   - Adjust thresholds based on actual usage
   - Add agency-specific matching rules as needed

### Data Quality

- Ensure consistent agency naming
- Standardize title formats where possible
- Keep Year field populated for all regulations
- Use the Superseded By/Supersedes fields for confirmed relationships

## 🔒 Security & Performance

- Script runs in Airtable's sandboxed environment
- No external API calls
- Processes one record at a time (triggered by changes)
- Read-only except for Internal Notes field
- Typical execution time: 1-3 seconds

## 📞 Support

**Technical Issues**: Contact your database administrator
**Script Updates**: Check this repository for latest version
**Airtable Support**: [Airtable Help Center](https://support.airtable.com)

## 📝 Version History

- **v1.0** (Current): Initial release with keyword-based matching

---

*Last updated: January 2025*