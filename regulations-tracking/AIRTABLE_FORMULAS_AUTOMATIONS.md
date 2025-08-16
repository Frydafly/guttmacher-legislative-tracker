# Airtable Formulas & Automations Setup Guide

**Purpose**: Practical formulas and minimal automation for regulation tracking
**Status**: Streamlined for actual database needs


## 🔢 Essential Formula Fields

### 1. **Reg-ID** (Core identifier)
```
CONCATENATE(State, "-REG-", Number, "-", Year)
```

### 2. **Emergency Expiration Check** (For emergency rules only)
**Field Type**: Formula
**Purpose**: Flag expired emergency regulations
```
IF(
  AND({Regulation Type} = "Emergency Rule", {Expiration Date}, IS_BEFORE({Expiration Date}, TODAY())),
  "⚠️ EXPIRED",
  ""
)
```
**Note**: This doesn't replace Current Status or Legal Status - it just flags expired emergencies that need attention


## 🤖 Single Automation: Supersedes Relationship Detector

### **Supersedes Relationship Detector**
**Trigger**: When record is created or updated (Title, State, or Agency changes)

**Script Action**: 
```javascript
// Find potential supersedes relationships
let table = base.getTable("Regulations");
let query = await table.selectRecordsAsync();
let currentRecord = inputConfig.record;

// Find similar regulations from same state/agency
let candidates = query.records.filter(record => {
    return record.id !== currentRecord.id &&
           record.getCellValue("State") === currentRecord.getCellValue("State") &&
           record.getCellValue("Issuing Agency") === currentRecord.getCellValue("Issuing Agency") &&
           record.getCellValue("Year") < currentRecord.getCellValue("Year");
});

// Check title similarity (simple keyword match)
let currentTitle = currentRecord.getCellValue("Title").toLowerCase();
let keywords = currentTitle.match(/\b(\w{4,})\b/g) || [];

let matches = candidates.filter(record => {
    let candidateTitle = record.getCellValue("Title").toLowerCase();
    let matchCount = keywords.filter(keyword => candidateTitle.includes(keyword)).length;
    return matchCount >= keywords.length * 0.5; // 50% keyword match
});

if (matches.length > 0) {
    // Add to Internal Notes field
    let notes = matches.map(r => `Potentially supersedes: ${r.getCellValue("Reg-ID")}`).join("\n");
    await table.updateRecordAsync(currentRecord.id, {
        "Internal Notes": notes
    });
}
```

**Purpose**: Identifies older regulations that might be replaced by new ones, helping maintain relationship tracking without manual review of every regulation

## 🔗 Managing the Supersedes Relationship (Simplified!)

You only need ONE linked record field to track both directions:

### Create "Superseded By" field:
- **Field Type**: Link to another record (Regulations table)
- **Purpose**: Link to the newer regulation that replaces this one
- **Auto-creates reverse field**: Called "Regulations" by default

### Rename the reverse field to "Supersedes":
- **What it shows**: Which older regulations this one replaces
- **Why this works**: One link field gives you both directions automatically!

### Example:
- Reg A (2023) is **Superseded By** → Reg B (2024)
- Reg B (2024) **Supersedes** → Reg A (2023) [shown in reverse field]

### Best Practice:
- Just create "Superseded By" and rename its reverse to "Supersedes"
- Don't create two separate link fields - it's redundant and confusing!

## 📊 Practical Views for Daily Use

### 1. **Active Regulations**
Filter: `OR({Current Status} = "Adopted", {Current Status} = "Effective", {Legal Status} = "In Effect")`
Group by: `{Agency Type}`
Sort: `{Effective Date}` (descending)

### 2. **Recently Modified**
Filter: `DATETIME_DIFF(TODAY(), {Last Modified}, 'days') < 30`
Sort: `{Last Modified}` (descending)

### 3. **By State Overview**
Group by: `{State}`
Sort: Count (descending)
Summary bar: Show count per state

### 4. **Unlinked to Policies**
Filter: `{Specific Policies Record Link} = BLANK() AND OR({Current Status} = "Adopted", {Current Status} = "Effective")`
Sort: `{Adopted Date}` (ascending - oldest first)

### 5. **By Agency View**
Group by: `{Issuing Agency}`
Sort: Alphabetical
Show: Parent Agency as secondary field

## 🔄 Additional Utility Formulas

### **Year-Quarter** (For trend analysis)
```
Year & "-Q" & 
IF(
  MONTH({Adopted Date}) <= 3, "1",
  IF(
    MONTH({Adopted Date}) <= 6, "2",
    IF(
      MONTH({Adopted Date}) <= 9, "3",
      "4"
    )
  )
)
```


### **Data Completeness Score** (Quality check)
```
(
  IF({Title}, 1, 0) + 
  IF({Issuing Agency Link}, 1, 0) + 
  IF({Current Status}, 1, 0) + 
  IF({Adopted Date}, 1, 0) + 
  IF({Specific Policies Record Link}, 1, 0)
) / 5 * 100 & "%"
```

## 📝 Implementation Order

1. **Create core formulas**: Reg-ID, Status Summary, Days Active
2. **Set up the supersedes detector automation**
3. **Create practical views** for daily operations
4. **Add utility formulas** as needed for specific analysis

---

**Key Principle**: Focus on formulas that surface actionable information and reduce manual cross-referencing. The single automation helps identify relationships that would otherwise require manual research.