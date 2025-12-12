# Airtable Schema Snapshot

**Captured**: 2025-12-12 11:03:34 UTC

**Base ID**: `appmy06ZrdLluxVD0`

## StateNet Raw Import

**Table ID**: `tbldlbeNNAlBdpKg0`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| StateNet Bill ID | formula | Formula field |
| Jurisdiction | singleLineText |  |
| Bill Type | singleLineText |  |
| Number | singleLineText |  |
| Special Session | singleLineText |  |
| Summary | multilineText |  |
| Year | singleLineText |  |
| Last Status Date | singleLineText |  |
| Abortion | singleLineText |  |
| AbortionBans | singleLineText |  |
| FamilyPlanning | singleLineText |  |
| Insurance | singleLineText |  |
| Minors | singleLineText |  |
| PeriodProducts | singleLineText |  |
| Pregnancy | singleLineText |  |
| Proactive | singleLineText |  |
| Newly Tracked | checkbox |  |
| Change in Status | checkbox |  |
| Import Time | createdTime |  |
| Imported By | createdBy |  |
| Linked Bill Record | multipleRecordLinks | Links to table tblCeDlrwrljIBCyi |

## Bills

**Table ID**: `tblCeDlrwrljIBCyi`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| BillID | formula | Formula field |
| Website Bill ID | formula | Formula field |
| State | singleSelect | Options: AL, AK, AZ... |
| BillType | singleSelect | Options: H, S, A... |
| BillNumber | number |  |
| Last Action | date |  |
| Introduction Date | date |  |
| Passed 1 Chamber Date | date |  |
| Passed Legislature Date | date |  |
| Enacted Date | date |  |
| Vetoed Date | date |  |
| Action Type | multipleSelects | Options: Legislation, Constitutional Amendment, Executive Order |
| Intent (access) | multipleSelects | Options: Protective, Restrictive, Neutral... |
| Specific Policies (access) | multipleSelects | Options: AB Ban 6to12 weeks LMP, AB Ban 13to15 weeks LMP, AB Ban 16to20 weeks LMP... |
| Website Blurb | multilineText |  |
| Description | richText |  |
| Internal Summary | richText |  |
| Current Bill Status | singleSelect | Options: Introduced, Passed First Chamber, Passed Both Chambers... |
| History | richText |  |
| Introduction Date Formula | formula | Formula field |
| Enacted Date Formula | formula | Formula field |
| Effective Date | date |  |
| Policy Categories (Access) | multipleSelects | Options: Abortion, Insurance Coverage, Pregnancy... |
| Prefiled | checkbox |  |
| Review Status | singleSelect | Options: Needs Review, In Progress, Complete |
| Last Action Date Formula | formula | Formula field |
| StateNet Raw Import | multipleRecordLinks | Links to table tbldlbeNNAlBdpKg0 |
| StateNet Imported Time | multipleLookupValues |  |
| Import Date | createdTime |  |
| Imported By | createdBy |  |
| Last Updated | lastModifiedTime |  |
| Last Updated By | lastModifiedBy |  |
| Specific Policies Record Link | multipleRecordLinks | Links to table tblQiscaIXZd6MzdV |
| Intent | multipleLookupValues |  |
| Specific Policies | multipleLookupValues |  |
| Headers | multipleLookupValues |  |
| Subcategories | multipleLookupValues |  |
| Policy Categories | multipleLookupValues |  |
| StateNet History | multilineText |  |
| Date Validation | formula | Formula field |
| Intent Issues | formula | Formula field |
| Category Intent | multipleLookupValues |  |
| Special Session | singleLineText |  |
| Regulations | multipleRecordLinks | Links to table tbl2cji7u0djZNxcV |
| Year | singleSelect | Options: 2025, 2026, 2025-2026... |
| Provisions | count |  |

## ACCESS VS BILLS

**Table ID**: `tblODJ2pnpfQHDtpT`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| BillID | multilineText |  |
| Migration Bills | multipleRecordLinks | Links to table tbluvDrkBPH5UM3Ve |
| Bills | singleLineText |  |
| Enacted in Access | multipleLookupValues |  |
| Enacted Date in Access | multipleLookupValues |  |
| Enacted Date in Airtable Bills | multipleLookupValues |  |
| Website Blurb in Access | multipleLookupValues |  |
| Website Blurb in Airtable Bills | multipleLookupValues |  |
| Access Legislation Field | multipleLookupValues |  |
| Access Const. Ammend. Field | multipleLookupValues |  |
| Action Type (from Bills) | multipleLookupValues |  |
| Access Bill Statuses | multipleLookupValues |  |
| Bill Status History in Airtable Bills | multipleLookupValues |  |

## Website Exports

**Table ID**: `tblKLbwlkKXhGrXyl`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| BillID | singleLineText |  |
| State | singleLineText |  |
| BillType | singleLineText |  |
| BillNumber | singleLineText |  |
| Ballot Initiative | singleLineText |  |
| Court Case | singleLineText |  |
| Subpolicy1 | singleLineText |  |
| Subpolicy2 | singleLineText |  |
| Subpolicy3 | singleLineText |  |
| Subpolicy4 | singleLineText |  |
| Subpolicy5 | singleLineText |  |
| Subpolicy6 | singleLineText |  |
| Subpolicy7 | singleLineText |  |
| Subpolicy8 | singleLineText |  |
| Subpolicy9 | singleLineText |  |
| Subpolicy10 | singleLineText |  |
| WebsiteBlurb | multilineText |  |
| Last Action Date | date |  |
| IntroducedDate | date |  |
| Passed1ChamberDate | date |  |
| Passed 2 Chamber | singleLineText |  |
| PassedLegislature | date |  |
| VetoedDate | date |  |
| EnactedDate | date |  |
| Vetoed | singleLineText |  |
| Enacted | singleLineText |  |
| Positive | singleLineText |  |
| Neutral | singleLineText |  |
| Restrictive | singleLineText |  |

## Access Migration

**Table ID**: `tbluvDrkBPH5UM3Ve`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| BillID | formula | Formula field |
| ID | number |  |
| State | singleSelect | Options: SC, OK, TN... |
| BillType | singleSelect | Options: H, S, CACR... |
| BillNumber | multilineText |  |
| BillDescription | multilineText |  |
| History | multilineText |  |
| Notes | multilineText |  |
| Calculation_Action Type | formula | Formula field |
| Calculate_Policy_Categories | formula | Formula field |
| Calculations_Subpolicies Combined | formula | Formula field |
| Also Track | multilineText |  |
| Was | multilineText |  |
| WebsiteBlurb | multilineText |  |
| Internal Summary | multilineText |  |
| Last Action Date | dateTime |  |
| Effective Date | dateTime |  |
| Calculated_bill status | formula | Formula field |
| Date Last Updated | multilineText |  |
| IntroducedDate | dateTime |  |
| Passed1ChamberDate | date |  |
| VetoedDate | dateTime |  |
| EnactedDate | dateTime |  |
| Calculated_Temperature Check | formula | Formula field |
| PassedLegislature | date |  |
| Full Bill Name | formula | Formula field |
| Legislation | number |  |
| Resolution | number |  |
| Ballot Initiative | number |  |
| Constitutional Amendment | number |  |
| Court Case | number |  |
| Abortion | number |  |
| Appropriations | number |  |
| C/W | number |  |
| Contraception | number |  |
| EC | number |  |
| Family Planning | number |  |
| Fetal Issues | number |  |
| Fetal Tissue | number |  |
| Incarceration | number |  |
| Insurance | number |  |
| Period Products | number |  |
| Pregnancy | number |  |
| Refusal | number |  |
| Repeals | number |  |
| Sex Ed | number |  |
| STIs | number |  |
| Youth | number |  |
| Subpolicy1 | singleSelect | Options: AB Ban All, AB Ban Genetic Anomaly, AB Misc Positive... |
| Subpolicy2 | singleSelect | Options: AB Misc Neutral, , INS Gender Affirming Care Coverage Restricted... |
| Subpolicy3 | singleSelect | Options: AB Coverage Private Plans Restricted, , Sex Ed LGBT Inclusive... |
| Subpolicy4 | singleSelect | Options: Pregnancy Misc Neutral, , Sex Ed LGBT Negative... |
| Subpolicy5 | singleSelect | Options: INS Contraceptive Coverage Mandated, , Minors Trans Parent Notice... |
| Subpolicy6 | singleSelect | Options: Repeals AB Ban Pre-Roe, , Repeals Physician Only... |
| Subpolicy7 | multilineText |  |
| Subpolicy8 | multilineText |  |
| Subpolicy9 | multilineText |  |
| Subpolicy10 | multilineText |  |
| Introduced | number |  |
| Passed 1 Chamber | number |  |
| Passed 2 Chamber | number |  |
| Awaiting Concurrance | number |  |
| In Conference | number |  |
| Out of Conference | number |  |
| On Govs Desk | number |  |
| Enacted | number |  |
| Vetoed | number |  |
| Line Item Vetoed | number |  |
| Veto Overridden | number |  |
| Resolution Adopted | number |  |
| Pending | number |  |
| Dead | number |  |
| Carryover to Next Year | number |  |
| Carryover from Last Year | number |  |
| Legislature Adjourned | number |  |
| EN | number |  |
| LM | number |  |
| OC | number |  |
| SN | number |  |
| ZAT | number |  |
| AB Spreadsheet | number |  |
| Chrons | number |  |
| Binders | number |  |
| EN Comments | number |  |
| Prefiled | number |  |
| Pushback | number |  |
| Positive | number |  |
| Neutral | number |  |
| Restrictive | number |  |
| Intent Issues | formula | Formula field |
| SSMA_TimeStamp | multilineText |  |
| Medication Abortion | number |  |
| Telehealth | number |  |
| ACCESS VS BILLS | multipleRecordLinks | Links to table tblODJ2pnpfQHDtpT |

## System Monitor

**Table ID**: `tblr91geZAZLnE4aW`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| Check Date | dateTime |  |
| Check Type | singleLineText |  |
| Bills Count | number |  |
| Bills by Status | multilineText |  |
| Bills Missing Info | number |  |
| Bills Missing Blurbs | number |  |
| Bills Missing Categories | number |  |
| Recently Modified | number |  |
| Last Export Date | dateTime |  |
| Export Count | number |  |
| New Bills Since Last Check | number |  |
| All States | multilineText |  |
| Active States | multilineText |  |
| Categories Coverage | multilineText |  |
| Status Changes Since Last Check | number |  |
| Intent Breakdown | multilineText |  |
| High Priority Items | number |  |
| Potential Issues | multilineText |  |
| Quality Score | number |  |
| Days Since Last Check | number |  |
| Related Import | singleLineText |  |
| Detailed Report | multilineText |  |

## Regulations

**Table ID**: `tbl2cji7u0djZNxcV`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| Reg-ID | formula | Formula field |
| State | singleSelect | Options: AR, CA, CO... |
| Number | number |  |
| Year | singleSelect | Options: 2021, 2022, 2023... |
| Regulation Type | singleSelect | Options: Standard Rulemaking, Emergency Rule, Temporary Rule... |
| Title | multilineText |  |
| Description | multilineText |  |
| Last Status Date Text | multilineText |  |
| Current Status | singleSelect | Options: Adopted, Under Review, Comment Period... |
| Auto Legal Status | formula | Formula field |
| Supersedes Detection | multilineText |  |
| Supersedes | multipleRecordLinks | Links to table tbl2cji7u0djZNxcV |
| Superseded By | multipleRecordLinks | Links to table tbl2cji7u0djZNxcV |
| History | multilineText |  |
| StateNet History | multilineText |  |
| Last Action Date | date |  |
| Introduction Date | date |  |
| Comment Period End | date |  |
| Comment Period Days Remaining | formula | Formula field |
| Adopted Date | date |  |
| Emergency Adopted Date | date |  |
| Effective Date | date |  |
| Expiration Date | date |  |
| Emergency Expiration Check | formula | Formula field |
| Specific Policies (access) | multipleSelects | Options: Misc, MaternalMortality, HIVTesting... |
| Specific Policies Record Link | multipleRecordLinks | Links to table tblQiscaIXZd6MzdV |
| Specific Policies | multipleLookupValues |  |
| Categories | multipleLookupValues |  |
| Subcategories | multipleLookupValues |  |
| Headers | multipleLookupValues |  |
| Intent | multipleLookupValues |  |
| Category Intent | multipleLookupValues |  |
| Policy Categories (Access) | multilineText |  |
| Issuing Agency Link | multipleRecordLinks | Links to table tblhKCL6uO2Qe7feq |
| Issuing Agency | multipleLookupValues |  |
| Agency Type | multipleLookupValues |  |
| Priority Level | multipleLookupValues |  |
| Parent Agency | multipleLookupValues |  |
| State Reg ID | multilineText |  |
| Citation | multilineText |  |
| Contact | multilineText |  |
| StateNet Link | multilineText |  |
| Related Bills | multipleRecordLinks | Links to table tblCeDlrwrljIBCyi |
| Legal Status | singleSelect | Options: In Effect, , Comment Period... |
| Review Status | singleSelect | Options: Needs Review |
| Website Blurb | multilineText |  |
| Internal Notes | multilineText |  |
| StateNet Regulations Import | multilineText |  |
| Import Date | createdTime |  |
| Last Updated | lastModifiedTime |  |
| Last Updated By | lastModifiedBy |  |
| Newly Tracked | checkbox |  |
| Change in Status | checkbox |  |
| Data Completeness Score | formula | Formula field |
| Last Action Date Formula | formula | Formula field |

## Agencies

**Table ID**: `tblhKCL6uO2Qe7feq`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| Agency Name | multilineText |  |
| Agency | singleSelect | Options: Bates Technical College, Bellevue College, Bellingham Technical College... |
| Agency Type | singleSelect | Options: Other, Professional Licensing Board, Health Department... |
| State | singleSelect | Options: WA, OR, KY... |
| Priority Level | singleSelect | Options: Low, High |
| Parent Agency | singleSelect | Options: Cabinet for Health and Family Services, Department of Banking and Insurance, Department of Corrections... |
| Notes | multilineText |  |
| Regulations | multipleRecordLinks | Links to table tbl2cji7u0djZNxcV |

## Policy Categories

**Table ID**: `tblQiscaIXZd6MzdV`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| Primary Key | formula | Formula field |
| Categories | singleSelect | Options: Abortion, , Contraception... |
| Subcategories | singleSelect | Options: Abortion bans, Targeted Regulation of Abortion Providers, Anti-abortion centers... |
| Headers | singleSelect | Options: Total ban, , Gestational duration ban before 18 weeks... |
| Specific Policies | singleSelect | Options: Total ban, Fetal personhood, 6wk ban... |
| Positive/Neutral/Restrictive | singleSelect | Options: Restrictive, Neutral, Positive... |
| Category Intent | singleSelect | Options: Abortion Restrictive, Abortion Neutral, Abortion Positive... |
| Bills | multipleRecordLinks | Links to table tblCeDlrwrljIBCyi |
| Bills Count | count |  |
| Category Intent Formula | formula | Formula field |
| Bills copy | singleLineText |  |
| Bills copy 2 | singleLineText |  |
| Imported table | multipleRecordLinks | Links to table tbl2cji7u0djZNxcV |

## Export Quality Reports

**Table ID**: `tblOWqbAQgwxo9WCy`

### Fields

| Field Name | Type | Description |
|------------|------|-------------|
| Export Date | dateTime |  |
| Quality Score | number |  |
| Grade | singleLineText |  |
| Total Records | number |  |
| Success Rate | number |  |
| Duration (seconds) | number |  |
| Completeness Score | number |  |
| Consistency Score | number |  |
| Date Errors | number |  |
| States Count | number |  |
| Recommendations | multilineText |  |
| Full Report | multilineText |  |
| Source Blurbs | number |  |
| Exported Blurbs | number |  |
| Blurb Failures | number |  |
| Blurb Fidelity | number |  |
| Critical Issues Ignored | singleLineText |  |
| Critical Issues Count | number |  |
| Critical Issues Details | multilineText |  |
| Accuracy Score | number |  |

