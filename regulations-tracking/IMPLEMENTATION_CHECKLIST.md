# Regulations Implementation Checklist

**Last Updated**: January 14, 2025

## ✅ COMPLETED - Ready for Import

### Data Preparation (DONE)
- [x] Analyzed Bills table structure to match format
- [x] Created transform script matching exact Airtable structure
- [x] Generated `regulations_airtable_import.csv` with all 96 regulations
- [x] Created `agencies_complete.csv` with all 62 unique agencies
- [x] Extracted all specific policies (Misc, lactation, Doula, MaternalMortality, etc.)
- [x] Mapped Comment Period End dates from Qualification Date field
- [x] Set up proper checkbox formatting ("checked" vs empty)
- [x] Determined Legal Status from Current Status
- [x] Preserved all agency names for linking

### Files Ready for Import
1. **`regulations_airtable_import.csv`** - Main regulations data (96 records)
2. **`agencies_complete.csv`** - Complete agencies lookup table (62 agencies)

## 🟢 What We Can Do NOW (Have All Info)

### Phase 1: Airtable Table Setup
- [ ] Import `agencies_complete.csv` to create Agencies table
- [ ] Import `regulations_airtable_import.csv` to create Regulations table
- [ ] Create these fields in Regulations table that match CSV:
  - [x] All fields are already in the CSV with correct names and formatting

### Phase 2: Configure Airtable Fields
- [ ] Set field types after import:
  - [ ] **Reg-ID** → Formula: `CONCATENATE(State,"-REG-",Number,"-",Year)`
  - [ ] **State** → Single Select
  - [ ] **Number** → Number field
  - [ ] **Year** → Number field
  - [ ] **Current Status** → Single Select
  - [ ] **Dates** → Date fields (all pre-formatted as YYYY-MM-DD)
  - [ ] **Issuing Agency Link** → Link to Agencies table
  - [ ] **Agency Type Lookup** → Lookup from Agencies
  - [ ] **Specific Policies Record Link** → Link to Policy Categories table
  - [ ] **Legal Status** → Single Select
  - [ ] **Review Status** → Single Select
  - [ ] **Newly Tracked** → Checkbox
  - [ ] **Change in Status** → Checkbox

### Phase 3: Link Records
- [ ] Link each regulation to its agency in Agencies table
- [ ] Link regulations to Policy Categories records based on "Specific Policies (access)" field
- [ ] Verify lookup fields are populating correctly

### Phase 4: Basic Automation
- [ ] Create "StateNet Regulations Import" table for raw imports
- [ ] Copy/adapt the bills import script structure for regulations
- [ ] Test with sample import from StateNet

## 🔴 Questions We NEED ANSWERED Before Proceeding

### Critical Setup Questions
1. **Airtable Access** ✅ RESOLVED
   - [x] Have access to the Airtable base
   - [ ] Confirm: Same base as Bills or separate base?
   - [ ] Create "Regulations" table
   - [ ] Create "StateNet Regulations Import" table

2. **StateNet Integration**
   - [ ] What's the exact format/structure of StateNet regulation exports?
   - [ ] How often do regulation updates come from StateNet? (Weekly like bills?)
   - [ ] Does StateNet provide a unique ID we should use as primary key?
   - [ ] **MOLLIE**: Does StateNet track legal challenges to regulations?

3. **Current Status Mapping**
   - [ ] The CSV has "Last Status Date" with text like "Rule Adoption - Secretary of State"
   - [ ] How should we parse this into our status categories?
   - [ ] Do we need all proposed statuses or should we simplify?

## 🟡 Questions That Would Be HELPFUL (Not Blockers)

### Workflow Questions
1. **Review Process**
   - [ ] Who will review regulations and assign Intent tags?
   - [ ] Same review workflow as bills or different process?
   - [ ] How often should regulations be reviewed?

2. **Reporting Needs**
   - [ ] Which reports/exports need to include regulations?
   - [ ] Should website export include regulations or keep separate?
   - [ ] Do partners want regulations in their email reports?

3. **Priority Regulations**
   - [ ] Any specific regulations needing immediate attention?
   - [ ] States with highest priority for regulation tracking?

### Data Quality Questions
1. **Agency Classification**
   - [ ] How to standardize agency names? (e.g., "Department of Human Services/Division of Children and Family Services")
   - [ ] Should we parse agency type from the full name?

2. **Policy Categorization**
   - [ ] Some regulations have policy fields like "Misc" - how to handle?
   - [ ] Should blank policy fields trigger review?

## 📋 Implementation Order

### Week 1: Setup (Can Start NOW)
1. Create Airtable tables with fields we understand
2. Import CSV data for testing
3. Document field mappings

### Week 2: Integration (Need StateNet Answers)
1. Build import automation
2. Test with real StateNet data
3. Set up scheduled imports

### Week 3: Enhancement (Need Workflow Answers)  
1. Add review workflows
2. Create views and filters
3. Build reports

### Week 4: Launch
1. Training
2. Go live
3. Monitor and adjust

## 🚨 Immediate Action Items

1. **TODAY**: Get access to Airtable base
2. **TODAY**: Schedule call with Mollie about StateNet
3. **THIS WEEK**: Import CSV as test data
4. **THIS WEEK**: Create basic table structure

## 📝 Notes from CSV Analysis

### Data Quality Observations
- All 96 records have "REGULATION" as Measure Type
- Dates use MM/DD/YYYY format consistently  
- Some contacts have full details, others just names
- Policy fields sometimes empty, sometimes duplicated
- State IDs follow various formats (need standardization?)

### Missing from CSV but Needed
- Current Status (only have "Last Status Date" with text)
- Intent tags (Protective/Restrictive/Neutral)
- Comment period dates
- Legal challenge status
- Related bills linkage

### Quick Stats
- 29 states represented
- 57 tagged with "Pregnancy"
- 32 newly tracked
- 92 with status changes
- Date range: 2024-2025

---

**Last Updated**: January 14, 2025
**Next Review**: After StateNet call with Mollie