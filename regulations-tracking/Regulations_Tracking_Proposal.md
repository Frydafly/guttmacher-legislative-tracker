# Regulations Tracking Proposal 

## Overview

Based on analysis of the 96 regulations currently being tracked in CSV format, I'm proposing we add regulations tracking to the Airtable database using a separate table structure that mirrors the existing Bills workflow where appropriate, with key additions for regulation-specific needs.

### Key Findings from Data Analysis:

- 96 regulations across 29 states  
- All are type "REGULATION" (vs bills which have H/S/etc.)  
- 57 regulations tagged with "Pregnancy" policy area  
- 32 newly tracked, 92 with status changes  
- Similar policy categorization to bills (Abortion, FamilyPlanning, Insurance, etc.)  
- Multiple issuing agencies (Health departments, licensing boards, insurance commissioners)  
- Both emergency and standard regulations present

## Recommended Structure: New "Regulations" Table

### Core Fields (Mirroring Bills Table)

**Identification:**

- **RegID** (Formula): `{State}-REG-{Number}-{Year}`  
- **State** (Single Select) \- use same state options as Bills  
- **Number** (Number) \- regulation number  
- **Year** (Number) \- year of regulation  
- **Title** (Long Text) \- full regulation title  
- **Description** (Rich Text) \- from StateNet "Summary"

**Status & History:**

- **Current Status** (Single Select):  
  - Proposed  
  - Comment Period (with end date tracking)  
  - Under Review  
  - Adopted  
  - Emergency Adopted  
  - Effective  
  - Withdrawn  
  - Challenged (legally)  
- **History** (Rich Text) \- for manual status updates  
- **StateNet History** (Multiline Text) \- from "Last Status Date"  
- **Last Action** (Date) \- automated from History  
- **Introduction Date** (Date)  
- **Comment Period End** (Date) \- critical for public participation  
- **Adopted Date** (Date)  
- **Emergency Adopted Date** (Date) \- immediate effect tracking  
- **Effective Date** (Date)  
- **Expiration Date** (Date) \- for emergency regulations

**Policy Classification (Same as Bills):**

- **Intent** (Multiple Select) \- Protective/Restrictive/Neutral  
- **Specific Policies Record Link** \- link to existing policies table  
- **Policy Categories** (Lookup) \- from linked policies  
- **Specific Policies (access)** (Multiple Select) \- same options as bills  
- **Policy Categories (Access)** (Multiple Select) \- for StateNet imports

### Regulation-Specific Fields

#### Regulation Type

- **Regulation Type** (Single Select):  
  - Standard Rulemaking  
  - Emergency Rule  
  - Temporary Rule  
  - Guidance/Bulletin

#### Agency Information

- **Issuing Agency** (Long Text) \- which department/board issued it  
- **Agency Type** (Single Select):  
  - Health Department *(Priority)*  
  - Professional Licensing Board *(Priority \- Medical/Pharmacist)*  
  - Insurance Commissioner *(Priority)*  
  - Medicaid Agency *(Priority)*  
  - Other  
- **State Reg ID** (Text) \- official state identifier  
- **Citation** (Text) \- regulatory citation  
- **Contact** (Long Text) \- regulatory contact information

#### Links & References

- **StateNet Link** (URL) \- link to StateNet record  
- **Related Bills** (Link to Records) \- connect to enabling legislation  
- **Supersedes** (Link to Records) \- link to previous regulation if replaced  
- **Superseded By** (Link to Records) \- link to newer regulation if replaced

#### Legal Status

- **Legal Status** (Single Select):  
  - In Effect  
  - Enjoined  
  - Under Challenge  
  - Vacated

### Process Fields (Same as Bills)

- **Review Status** (Single Select) \- Needs Review/In Progress/Complete  
- **Website Blurb** (Multiline Text) \- if needed for website  
- **Internal Notes** (Rich Text)  
- **StateNet Import Link** (Link to Records) \- to Regulations Import table  
- **Import Date** (Created Time)  
- **Last Updated** (Modified Time)  
- **Updated By** (Collaborator)

## New "StateNet Regulations Import" Table

Similar to existing StateNet Raw Import, with all CSV fields mapped directly.

## Implementation Decisions Based on Feedback

### 1\. Scope & Tracking

**Decision**: Track **state regulations only** (not federal or local/municipal)

- *Candace confirmed: "Just state should be tracked"*

### 2\. Priority Agencies

**Decision**: Focus on high-priority agencies with specific tracking:

- Health Departments ✓  
- Medicaid Agencies ✓  
- Medical and Pharmacist Licensing Boards ✓  
- Insurance Commissioners ✓  
- *As noted by Candace: These are the priority agencies for tracking*

### 3\. Historical Data

**Decision**: Import only the 96 regulations from current CSV

- *Candace confirmed: "I don't think we need historical data beyond what's in the current CSV"*

### 4\. Policy Classification

**Decision**: Use the same policy categorization system as bills

- Intent tags (Protective/Restrictive/Neutral) assigned during review  
- *Candace agreed with this approach*

### 5\. Comment Period Tracking

**Decision**: Include comment period fields for future use

- *Candace noted: "Guttmacher hasn't historically done this but I think it's important to have that option in case we want to do so in the future"*

### 6\. Legal Challenge Tracking

**Action Item**: Follow up with Mollie about StateNet coverage

- *Candace noted: "I don't know if State Net picks this up but we should follow up with Mollie on this"*  
- Include Legal Status field as placeholder pending confirmation

### 7\. Workflow Integration

**Decision**: Mirror bills workflow where possible:

- Weekly StateNet imports (assuming same frequency as bills)  
- Same review status process  
- Similar internal notes and tracking fields

## Additional Features to Implement

### Automation Opportunities

1. **Comment Period Alerts**: Automated reminders when comment periods are ending  
2. **Emergency Regulation Expiration**: Track and alert on emergency rules about to expire (60-180 days)  
3. **Agency Prioritization**: Filter/sort views by priority agencies  
4. **Legal Challenge Updates**: If StateNet provides, automate tracking

### Reporting Views

1. **Active Regulations Dashboard**: All regulations currently in effect  
2. **Emergency Rules Tracker**: Emergency regulations with expiration dates  
3. **Comment Period Calendar**: Upcoming comment deadlines  
4. **Agency-Specific Views**: Filtered by priority agencies  
5. **Combined Policy Actions**: Unified view of bills and regulations

## Next Steps

### Phase 1: Initial Setup 

1. ✅ Confirm table structure with team  
2. Create Regulations table in Airtable  
3. Create StateNet Regulations Import table  
4. Set up basic field configurations

### Phase 2: Data Import

1. Import 96 regulations from CSV  
2. Map StateNet fields to Airtable fields  
3. Validate data quality and completeness  
4. Review and assign Intent tags

### Phase 3: Automation

1. Build import automation script  
2. Test with sample StateNet data  
3. Set up scheduled imports  
4. Create alert automations

## Open Questions for Follow-up

1. **Mollie**: Does StateNet track legal challenges to regulations?  
2. **Team**: Frequency of StateNet regulation updates (weekly like bills?)  
3. **Team**: Any specific regulations that need immediate attention?  
4. **Team**: Preferred format for comment period alerts?

## Data Quality Notes from CSV Analysis

- Some regulations show duplicate policy values (e.g., "STIs; STIs") \- needs cleanup  
- Date formats are consistent (MM/DD/YYYY)  
- All regulations have StateNet IDs for linking  
- Priority states appear to be those with most regulations (CA, NY, etc.)

### Questions for Implementation

### 1\. Workflow & Process

- How often do you receive regulatory updates from StateNet? Weekly like bills?  
- Are you tracking the comment period deadlines to alert for public participation opportunities? **Guttmacher hasn't historically done this but I think it's important to have that option in case we want to do so in the future.**

### 2\. Status Tracking

- Are the proposed status options comprehensive enough?  
- How important is tracking emergency regulations differently (they can take effect immediately)?  
- Do you need alerts when emergency regulations are about to expire (typically 60-180 days)?  
- Should we track legal challenges to regulations? **I don't know if State Net picks this up but we should follow up with Mollie on this.**

### 3\. Agency Tracking

- Do you need to track/report by issuing agency (health dept vs licensing board vs insurance)? **Yes**  
- Some regulations come from multiple agencies \- how should we handle this?  
- Are there specific agencies whose regulations are higher priority?  **I would say health departments/medicaid agencies/and medical and pharmacist licensing boards would be priorities. and insurance commissioners**

### 4\. Policy Classification

- Should regulations use the exact same policy categorization system as bills?  
- Since regulations don't come with Intent tags (Protective/Restrictive/Neutral), should these be assigned during review?  
- Some regulations show duplicate values (e.g., "STIs; STIs") \- is this intentional?  
- Do you track implementation impact differently than legislative intent?

### 5\. Reporting & Outputs

- Do you need regulation-specific reports (e.g., "emergency rules in effect")?  
- Should we create a combined "all policy actions" view mixing bills and regs?

### 6\. Data Relationships

- Some regulations implement specific bills \- should we create linking fields?  
- Should federal regulations be tracked, or just state? ***Just state should be tracked.***  
- How should we handle local/municipal regulations if any?  
- Do you track when one regulation supersedes another?

### 7\. Historical Data & Priority

- Should we import all 96 regulations from the CSV as a starting point? **Agree**  
- Do you need historical regulation data beyond what's in the current CSV? **I don't think we need historical data beyond what's in the current CSV.**

## Next Steps

1. **Confirm table structure** \- I can create the tables once you approve the structure  
2. **Build import automation** \- Following the same pattern as bills import  
3. **Test with sample data** \- Import a few regulations to test workflow  
4. **Train team** \- Quick session on any regulation-specific processes

