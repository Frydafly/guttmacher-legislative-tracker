# Airtable Formulas & Automations Setup Guide

**Purpose**: Set up automations and formulas now that data import is complete
**Status**: Ready to implement in Airtable


## 🔢 Recommended Formula Fields

### 1. **Reg-ID** (Already exists, but verify formula)
```
CONCATENATE(State, "-REG-", Number, "-", Year)
```

### 2. **Days Until Expiration** (NEW - Create this!)
**Field Type**: Formula
**Purpose**: Shows countdown for emergency rules
```
IF(
  AND({Regulation Type} = "Emergency Rule", {Expiration Date}),
  DATETIME_DIFF({Expiration Date}, TODAY(), 'days'),
  BLANK()
)
```
**Returns**: Number of days until expiration (negative if expired)

### 3. **Expiration Status** (NEW - Create this!)
**Field Type**: Formula
**Purpose**: Visual indicator of expiration status
```
IF(
  AND({Regulation Type} = "Emergency Rule", {Expiration Date}),
  IF(
    DATETIME_DIFF({Expiration Date}, TODAY(), 'days') < 0,
    "🔴 EXPIRED",
    IF(
      DATETIME_DIFF({Expiration Date}, TODAY(), 'days') < 30,
      "🟡 Expiring Soon",
      "🟢 Active"
    )
  ),
  ""
)
```

### 4. **Auto Legal Status** (NEW - Alternative to imported field)
**Field Type**: Formula
**Purpose**: Automatically determine legal status from dates and status
```
IF(
  AND({Regulation Type} = "Emergency Rule", {Expiration Date}),
  IF(
    IS_BEFORE({Expiration Date}, TODAY()),
    "Expired",
    IF(
      OR({Current Status} = "Adopted", {Current Status} = "Effective"),
      "In Effect",
      {Current Status}
    )
  ),
  IF(
    OR({Current Status} = "Adopted", {Current Status} = "Effective"),
    "In Effect",
    IF(
      {Current Status} = "Proposed",
      "Pending",
      IF(
        {Current Status} = "Comment Period",
        "Comment Period",
        "Under Review"
      )
    )
  )
)
```

### 5. **Comment Period Days Remaining** (NEW)
**Field Type**: Formula
**Purpose**: Track comment period deadlines
```
IF(
  AND({Current Status} = "Comment Period", {Comment Period End}),
  DATETIME_DIFF({Comment Period End}, TODAY(), 'days'),
  BLANK()
)
```

### 6. **Priority Alert** (NEW - Better than Needs Review Flag)
**Field Type**: Formula
**Purpose**: Shows what needs immediate attention
```
IF(
  AND({Regulation Type} = "Emergency Rule", {Days Until Expiration} < 30),
  "🔴 Expiring Soon",
  IF(
    AND({Current Status} = "Comment Period", {Comment Period Days Remaining} < 7),
    "🟡 Comment Closing",
    IF(
      BLANK({Specific Policies Record Link}),
      "🔵 Link Policies",
      ""
    )
  )
)
```
**Note**: This is more specific than Review Status - shows WHY something needs attention

## 🤖 Essential Automations to Create

### 1. **Emergency Rule Expiration Alert**
**Trigger**: When record matches conditions
- Regulation Type = "Emergency Rule"
- Days Until Expiration = 30

**Action**: 
- Update Review Status to "Urgent"
- Add note to Internal Notes: "⚠️ Emergency rule expires in 30 days - {Expiration Date}"
- Create task in project management system (if integrated)

### 2. **Comment Period Ending Alert**
**Trigger**: When record matches conditions
- Current Status = "Comment Period"
- Comment Period Days Remaining = 7

**Action**:
- Update Review Status to "Urgent"
- Add note to Internal Notes: "📝 Comment period ends {Comment Period End}"
- Update Priority Alert field (if using formula)

### 3. **New Regulation Assignment**
**Trigger**: When record is created

**Action**:
- Set Review Status to "Needs Review"
- Assign to team member based on State or Agency Type (if using collaborator field)
- Add timestamp to Internal Notes: "Added {Date}"

### 4. **Status Change Logger**
**Trigger**: When {Current Status} is updated

**Action**:
- Append to History field with:
  ```
  [{Date}] Status changed to {Current Status} - {Last Status Date Text}
  ```
- Update Last Action Date to TODAY()

### 5. **Auto-Expire Emergency Rules**
**Trigger**: Daily at 9am

**Condition**: 
- Regulation Type = "Emergency Rule"
- Expiration Date is before TODAY()
- Legal Status ≠ "Expired"

**Action**:
- Update Legal Status to "Expired"
- Update Current Status to "Expired"
- Add note to Internal Notes: "Auto-expired on {Date}"

### 6. **Policy Linking Check**
**Trigger**: Weekly on Monday

**Condition**: Specific Policies Record Link is empty

**Action**: 
- Update Review Status to "Needs Policy Link"
- Create filtered view showing all unlinked regulations
- Optional: Send Slack notification with count of unlinked records

### 7. **Supersedes Relationship Detector**
**Trigger**: When new record created

**Action**: Find records where:
- Same State
- Same Agency
- Similar Title (using fuzzy match)
- Earlier Year

**Suggest**: Potential supersedes relationships for review

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

## 📊 Recommended Views with Filters

### 1. **Emergency Rules Dashboard**
Filter: `{Regulation Type} = "Emergency Rule"`
Sort: `{Days Until Expiration}` (ascending)
Color coding: Based on `{Expiration Status}`

### 2. **Comment Period Active**
Filter: `{Current Status} = "Comment Period"`
Sort: `{Comment Period End}` (ascending)
Show: Comment period countdown prominently

### 3. **Needs Policy Linking**
Filter: `{Specific Policies Record Link} = BLANK()`
Group by: `{Agency Type}`
Sort: `{Adopted Date}` (newest first)
Helper column: Show `{Specific Policies (access)}` to guide linking

### 4. **Expired Regulations**
Filter: `{Legal Status} = "Expired"`
Sort: `{Expiration Date}` (newest first)

### 5. **High Priority Agencies**
Filter: `{Priority Level (from Issuing Agency Link)} = "High"`
Group by: `{Agency Type}`

## 🔄 Data Maintenance Formulas

### Calculate Expiration Date (if not imported)
**Field**: Expiration Date (Formula instead of Date field)
```
IF(
  {Regulation Type} = "Emergency Rule",
  IF(
    {Emergency Adopted Date},
    DATEADD({Emergency Adopted Date}, 180, 'days'),
    IF(
      {Effective Date},
      DATEADD({Effective Date}, 180, 'days'),
      BLANK()
    )
  ),
  IF(
    {Regulation Type} = "Temporary Rule",
    IF(
      {Effective Date},
      DATEADD({Effective Date}, 90, 'days'),
      BLANK()
    ),
    BLANK()
  )
)
```

### Auto-Detect Regulation Type (if not imported)
**Field**: Regulation Type Detection (Formula)
```
IF(
  {Emergency Adopted Date},
  "Emergency Rule",
  IF(
    OR(
      FIND("emergency", LOWER({StateNet History})),
      FIND("emergency", LOWER({Title}))
    ),
    "Emergency Rule",
    IF(
      OR(
        FIND("temporary", LOWER({StateNet History})),
        FIND("temp", LOWER({Title}))
      ),
      "Temporary Rule",
      IF(
        OR(
          FIND("guidance", LOWER({Title})),
          FIND("bulletin", LOWER({Title}))
        ),
        "Guidance/Bulletin",
        "Standard Rulemaking"
      )
    )
  )
)
```

## 💡 Pro Tips

1. **Use Lookup Fields**: Instead of duplicating data, use lookups from linked records
   - Agency Type, Priority Level, Parent Agency all come from Agencies table

2. **Color Coding**: Use conditional colors based on:
   - Expiration Status (Red/Yellow/Green)
   - Legal Status (different colors for In Effect/Expired/Challenged)
   - Review Status (highlight "Needs Review")

3. **Button Fields**: Add buttons for common actions:
   - "Mark Reviewed" - Updates Review Status and adds timestamp
   - "Request Intent Review" - Sends to policy team
   - "Check for Updates" - Triggers StateNet sync

4. **Rollup Fields**: For agencies, add rollups to count:
   - Total regulations
   - Active regulations
   - Expired regulations
   - Regulations needing review

## 🚨 Critical Automations Priority

**Must Have** (No emails, just status updates):
1. Emergency Rule Expiration Alert - Updates Review Status
2. Auto-Expire Emergency Rules - Daily status check
3. Comment Period Ending Alert - Flags urgent items

**Should Have**:
4. New Regulation Assignment - Sets initial status
5. Policy Linking Check - Weekly review flag

**Nice to Have**:
6. Status Change Logger - Audit trail
7. Supersedes Relationship Detector - Finds relationships

**Note**: All automations update fields/status rather than sending emails

## 📝 Implementation Order

1. **First**: Create formula fields (they're instant)
2. **Second**: Set up critical automations
3. **Third**: Create filtered views
4. **Fourth**: Add nice-to-have automations
5. **Finally**: Configure color coding and formatting

---

**Remember**: These formulas and automations eliminate the need for Python scripts after initial import!