# Legislative Tracker Dashboard Enhancement Plan

## Current State Analysis

Based on screenshots, you have a well-structured Airtable Interface with:
- **Page 1 (Bills Overview)**: Total counts, bills by state bar chart, status/intent/action type charts, temporal trends
- **Page 2 (Bills Details)**: Detailed table view with filters for State, Action Type, BillType, Policy Categories, Subcategories
- **Page 3 (Policy Categories)**: Policy category analysis, specific policies table, category+intent combinations

### Tables Identified (from code analysis):
- **Bills** - Main table with fields: BillID, State, BillType, BillNumber, Intent, Specific Policies, Website Blurb, dates (Introduction, Passed 1 Chamber, Enacted, etc.), Action Type, Status
- **Policy Categories** - Linked to Bills for categorization
- **Export Quality Reports** - Tracks data quality metrics
- **Website Exports** - Stores exported data

## Enhancement Requirements → Implementation Plan

### 1. ✅ **Topline Summaries with Trend Analysis**
**Status: CAN DO THIS**

**Current gap**: No narrative text, no year-over-year comparison

**Implementation**:
1. Add **Rich Text element** at top of Page 1 with placeholder narrative
2. Create formula fields in Bills table:
   - `Protective_Restrictive_Ratio` = COUNT(Intent="Positive") / COUNT(Intent="Restrictive")
   - `YoY_Change` = Compare with historical data (needs historical snapshot table)
3. Add **Number elements** showing:
   - Total bills introduced (exists)
   - Protective vs Restrictive ratio (new)
   - % change from last session (new)

**What you need to build**:
- Historical snapshots table to store weekly/monthly counts for comparisons
- Automation to capture snapshot data

---

### 2. ⚠️ **Table of Contents Navigation**
**Status: PARTIAL - QUESTIONS**

**Current structure**: Already has 3 pages (Bills Overview, Bills Details, Policy Categories)

**Enhancement options**:
1. **Option A**: Add more pages for each major category
   - Create pages for: Abortion, Contraception, Trans Health, Youth
   - Use Interface navigation sidebar (already exists)

2. **Option B**: Enhanced filtering on existing pages
   - Add **Button Bar element** with preset filters
   - Each button applies specific category filter
   - Users stay on same page but view updates

**Recommendation**: Option B - less maintenance, better performance

---

### 3. ⚠️ **Session Snapshot Visual**
**Status: PARTIAL**

**Current capability**: You have temporal charts but not session progress indicators

**Enhancement**:
1. Create new Interface section on Page 1
2. Add these elements:
   - **Progress bar**: % of session elapsed
   - **Number grid**: Bills at each stage (Introduced → Committee → Passed 1st → Enacted)
   - **Velocity chart**: Bills moving per week

**Implementation steps**:
```
- Add formula field: Session_Progress = DATETIME_DIFF(TODAY(), Session_Start) / Session_Length
- Create filtered views for each status
- Use Number elements with conditional formatting
```

---

### 4. ✅ **Policy Resource Links**
**Status: CAN DO THIS**

**Implementation**:
1. Add `Resource_URL` field to Policy Categories table
2. Add `Resource_Description` field
3. On Policy Categories page, add **List element** showing resources
4. Use **Button elements** with "Open URL" action

---

### 5. 🔄 **Interactive Map → State Grid**
**Status: ALTERNATIVE SOLUTION**

**State Grid Implementation** (MVP):
1. Create new Interface page: "Geographic View"
2. Use **Button Grid** - 50 buttons in 10x5 layout
3. Each button:
   - Shows state abbreviation
   - Color coded by bill count/activity
   - Click to filter Bills view to that state

**Visual mockup**:
```
[AK-5] [AL-19] [AR-27] [AZ-38] [CA-26]
[CO-28] [CT-27] [DE-15] [FL-31] [GA-22]
... (arranged geographically or alphabetically)
```

**Future enhancement**: Link to external interactive map tool

---

## Implementation Roadmap

### Week 1: Foundation
- [ ] Create historical snapshots table
- [ ] Add formula fields for ratios and trends
- [ ] Add rich text narrative section with placeholders
- [ ] Set up automation for weekly snapshots

### Week 2: Navigation & Organization
- [ ] Implement button bar for category filtering
- [ ] Create saved filter combinations
- [ ] Add resource links to Policy Categories
- [ ] Test filter performance with full dataset

### Week 3: Visualizations
- [ ] Build session snapshot section
- [ ] Create state grid layout
- [ ] Add progress indicators
- [ ] Implement conditional formatting

### Week 4: Polish & Testing
- [ ] User testing with stakeholders
- [ ] Performance optimization
- [ ] Documentation
- [ ] Training materials

---

## Technical Requirements

### New Airtable Components Needed:
1. **Historical Snapshots Table**
   ```
   Fields:
   - Snapshot_Date (Date)
   - Total_Bills (Number)
   - Bills_By_Status (Long text/JSON)
   - Bills_By_Intent (Long text/JSON)
   - Bills_By_State (Long text/JSON)
   ```

2. **Automation Script** (weekly snapshot)
   ```javascript
   // Runs weekly to capture metrics
   const bills = await billsTable.selectRecordsAsync();
   const snapshot = {
     date: new Date(),
     totalBills: bills.records.length,
     byStatus: groupByStatus(bills),
     byIntent: groupByIntent(bills)
   };
   await snapshotsTable.createRecordAsync(snapshot);
   ```

3. **Formula Fields in Bills Table**
   - Session progress calculations
   - Ratio calculations
   - Trend indicators

### Interface Elements to Add:
- Rich text blocks (narrative summaries)
- Button bars (navigation/filtering)
- Number grids (metrics display)
- Progress bars (session tracking)
- State grid (50-button layout)

---

## Questions to Resolve

1. **Historical data**: How far back should comparisons go?
2. **Update frequency**: Real-time vs daily vs weekly snapshots?
3. **State grid layout**: Geographic or alphabetical arrangement?
4. **Category hierarchy**: Which categories need dedicated pages?
5. **Access permissions**: Different views for different user groups?

---

## Alternative Solutions

If Airtable Interface limitations become blockers:

### Recommended: **Softr.io**
- Built specifically for Airtable
- Supports custom HTML/CSS
- Can embed maps
- $49/month for basic plan
- No coding required

### For more control: **Custom HTML Dashboard**
- Use existing website-export.js as data source
- Host on existing website
- Full design flexibility
- Requires maintenance

---

## Next Steps

1. **Immediate actions**:
   - Create Historical Snapshots table
   - Add test formula fields
   - Mock up state grid with 5-10 states

2. **This week**:
   - Get stakeholder feedback on state grid vs map
   - Confirm priority features
   - Begin Week 1 implementation

3. **Success metrics**:
   - Dashboard loads in <3 seconds
   - All metrics update automatically
   - Users can navigate to any category in 2 clicks
   - State-level data accessible in 1 click