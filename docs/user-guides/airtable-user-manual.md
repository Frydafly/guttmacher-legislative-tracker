# Policy Tracker Database: User Manual

## Table of Contents

1.  [[System Overview]{.underline}](#system-overview)

2.  [[Getting Started]{.underline}](#getting-started)

3.  [[Tables & Structure]{.underline}](#tables-structure)

4.  [[Importing StateNet Data]{.underline}](#importing-statenet-data)

5.  [[Bill Processing Workflow]{.underline}](#bill-processing-workflow)

6.  [[Policy Categorization]{.underline}](#policy-categorization)

7.  [[Website Content
    Preparation]{.underline}](#website-content-preparation)

8.  [[Exporting Data]{.underline}](#exporting-data)

9.  [[Common Searches & Reports]{.underline}](#common-searches-reports)

10. [[Automations & Scripts]{.underline}](#automations-scripts)

11. [[Troubleshooting]{.underline}](#troubleshooting)

## System Overview

The Guttmacher Policy Tracker is an Airtable-based system for tracking
state-level legislation related to sexual and reproductive health and
rights. The system processes CSV data from StateNet, enables policy
analysis and categorization, manages website content updates, and
generates partner reports.

### Key Workflow

1.  StateNet CSV data is imported into the StateNet Raw Import table

2.  Automation creates/updates corresponding records in the Bills table

3.  Policy team reviews and categorizes bills in the Bills table

4.  Bills requiring publication are prepared with website blurbs

5.  Website-ready content is exported via script to Website Exports
    table

6.  Regular reports are generated for partners

## Getting Started

### Accessing the System

- Log in to Airtable using your Guttmacher email

- Navigate to the Policy Tracker base

- Select the appropriate table view based on your task

### Main Tables Overview

- **StateNet Raw Import**: Initial landing place for StateNet CSV data

- **Bills**: Main policy tracking and categorization

- **Policy Categories**: Master list of policy categories and
  subcategories

- **Website Exports**: Formatted data for website publication

## Tables & Structure

### StateNet Raw Import

*Purpose: Initial landing place for StateNet CSV data*

Key fields from StateNet CSV:

- **StateNet Bill ID**: Unique identifier (becomes BillNumber in Bills
  table)

- **Jurisdiction**: State abbreviation (becomes State in Bills table)

- **Bill Type**: H, S, etc. (becomes BillType in Bills table)

- **Number**: Bill number

- **Summary**: Bill description (becomes Description in Bills table)

- **Last Status Date**: Latest action information (becomes History in
  Bills table)

- **Category flags**: Abortion, AbortionBans, FamilyPlanning, Insurance,
  etc.

- **Import Time**: When record was imported

- **Imported By**: Who imported the record

- **Linked Bill Record**: Links to corresponding Bills table record

### Bills

*Purpose: Main policy tracking and categorization*

**Basic Information:**

- **BillID**: Formula field combining State-BillType-BillNumber

- **State**: Single select field with all US state abbreviations

- **BillType**: Single select indicating where bill originated (see
  BillType reference below)

- **BillNumber**: Number assigned by state legislature

- **Description**: Bill summary from StateNet (auto-populated from Raw
  Import)

- **Internal Summary**: Manually written staff summary

- **History**: Legislative action history from StateNet

- **StateNet History**: Additional StateNet status information

**Status & Dates:**

- **Current Bill Status**: Formula-derived current status (Introduced,
  Dead, Legislature Adjourned, Passed First Chamber, Awaiting
  Concurrence, Passed Both Chambers, In Conference, Enacted, Vetoed)

- **Prefiled**: Checkbox indicating if bill was prefiled

- **Last Action**: Date field (auto-populated by Last Action Date
  Formula)

- **Last Action Date Formula**: Hidden formula field that extracts most
  recent date

- **Introduction Date**: Date field (auto-populated by Introduction Date
  Formula)

- **Introduction Date Formula**: Hidden formula field that extracts
  introduction date

- **Passed 1 Chamber Date**: Date field (auto-populated by formula)

- **Passed Legislature Date**: Date field (manually entered if needed)

- **Enacted Date**: Date field (auto-populated by Enacted Date Formula)

- **Enacted Date Formula**: Hidden formula field that extracts enactment
  date

- **Vetoed Date**: Date field (auto-populated by formula)

- **Effective Date**: Date field (manually entered)

- **Date Validation**: Formula field that flags any future dates with
  warning

#### BillType Reference

- **H**: Standard legislation introduced in a state\'s House of
  Representatives

- **S**: Standard legislation introduced in a state\'s Senate

- **A**: Standard legislation introduced in state Assemblies (used in
  states like NY, CA, WI, NV)

- **SJR**: Senate Joint Resolution - Used for constitutional amendments
  or major policy statements

- **CACR**: Constitutional Amendment Concurrent Resolution -
  Specifically for state constitutional amendments

- **HJR**: House Joint Resolution - Similar to SJR but initiated in
  House

- **LR**: Legislative Resolution - General resolution from either
  chamber

- **D**: Draft Bill - Preliminary version not yet formally introduced

- **SR**: Senate Resolution - Resolution involving only Senate

- **HM**: House Memorial - Formal statement or petition from House

- **ACR**: Assembly Concurrent Resolution - Needs both chambers but not
  governor\'s signature

- **HD**: House Document - Formal document or draft bill in House

- **LSR**: Legislative Service Request - Request for legislation to be
  drafted (common in New Hampshire)

- **SCR**: Senate Concurrent Resolution - Needs both chambers but not
  governor\'s signature

**Policy Classification:**

- **Action Type**: Legislation, Constitutional Amendment, etc.

- **Intent**: Protective, Restrictive, Neutral

- **Specific Policies**: Multiple select linked to Policy Categories
  table

- **Specific Policies Record Link**: Linked records to Policy Categories

- **Policy Categories**: Auto-populated from Specific Policies

- **Subcategories**: Auto-populated from Specific Policies

- **Headers**: Auto-populated from Specific Policies

- **Category Intent**: Auto-populated from Specific Policies

**Review & Publishing:**

- **Review Status**: Needs Review, In Progress, Complete

- **Website Blurb**: Public-facing description for website

- **Internal Notes**: Staff notes

- **Review Notes**: Notes from review process

**System Fields:**

- **Import Date**: When bill was first imported

- **Imported By**: Who imported the bill

- **Last Updated**: Most recent update

- **Last Updated By**: Who made most recent update

- **StateNet Raw Import**: Link back to import record

- **Date Validation**: Formula field checking for date errors

### Policy Categories

*Purpose: Master list of policy categories and hierarchical
relationships*

Key fields:

- **Primary Key**: Unique identifier for each policy

- **Categories**: Main category (Abortion, Contraception, etc.)

- **Subcategories**: Second-level categorization

- **Headers**: Third-level categorization

- **Specific Policies**: Detailed policy description

- **Positive/Neutral/Restrictive**: Intent classification

- **Category Intent Formula**: Auto-generated intent with category

- **Category Intent**: Final intent classification

- **Bills**: Linked records showing which bills use this policy

- **Bills Count**: Number of bills using this policy

### Website Exports

*Purpose: Formatted data created by export script for website
publication*

Key fields:

- **State**: State abbreviation

- **BillType**: Bill type

- **BillNumber**: Bill number

- **Ballot Initiative**: 0/1 flag

- **Court Case**: 0/1 flag

- **Subpolicy1-10**: Individual policy components

- **WebsiteBlurb**: Public description

- **Last Action Date**: Most recent action date

- **IntroducedDate**: Introduction date

- **Passed1ChamberDate**: First chamber passage date

- **Passed 2 Chamber**: Second chamber passage date

- **PassedLegislature**: Legislature passage date

- **VetoedDate**: Veto date

- **EnactedDate**: Enactment date

- **Vetoed**: 0/1 flag

- **Enacted**: 0/1 flag

- **Positive**: 0/1 flag (based on Intent)

- **Neutral**: 0/1 flag (based on Intent)

- **Restrictive**: 0/1 flag (based on Intent)

## Importing StateNet Data

### Import Process

1.  Navigate to StateNet Raw Import table

2.  Click \"+\" to add new records or use CSV import

3.  Map fields according to standard mapping:

    - Jurisdiction → Jurisdiction

    - Bill Type → Bill Type

    - StateNet Bill ID → StateNet Bill ID

    - Summary → Summary

    - Last Status Date → Last Status Date

4.  Confirm import

### What Happens Automatically

When a new record is created in StateNet Raw Import, the \"Process
StateNet Import\" automation:

1.  **Searches for existing bill**: Looks in Bills table for matching
    BillID (StateNet Bill ID)

2.  **If no existing bill found**:

    - Creates new record in Bills table

    - Maps Summary → Description

    - Maps Last Status Date → History

    - Links Raw Import record to new Bills record

3.  **If existing bill found**:

    - Updates the existing Bills record with new information

    - Updates History field with new status information

    - Links Raw Import record to existing Bills record

### Post-Import Review

1.  Check Bills table for new records (look for \"Needs Review\" status)

2.  Review automatically populated fields for accuracy

3.  Begin manual categorization process

## Bill Processing Workflow

### Initial Review Process

1.  Navigate to Bills table, \"Needs Review\" view

2.  For each new bill:

    - Review Description field (auto-populated from StateNet)

    - Decide if bill should be tracked for SRHR content

    - If yes, change Review Status to \"In Progress\"

    - If no, change Review Status to \"Not Tracked\" or similar

### Required Manual Fields

When processing a bill, staff must fill in:

**Policy Classification (Required):**

- **Action Type**: Select from dropdown (Legislation, Constitutional
  Amendment, etc.)

- **Specific Policies**: Select from linked Policy Categories (this
  auto-populates other category fields)

**Content Creation:**

- **Internal Summary**: Write concise staff summary of bill content

- **Website Blurb**: Write public-facing description (for enacted/vetoed
  bills)

**Additional Information (As Needed):**

- **Effective Date**: Enter if different from enactment date

- **Internal Notes**: Any additional context or notes

- **Review Notes**: Comments from review process

### Automatic Field Population

The following fields are automatically populated by formulas:

- **BillID**: Combines State-BillType-BillNumber

- **Current Bill Status**: Derived from History field

- **Last Action**: Extracted from History field

- **Introduction Date**: Extracted from History field

- **Enacted Date**: Extracted from History field

- **Vetoed Date**: Extracted from History field

- **Policy Categories**: Auto-populated from Specific Policies selection

- **Subcategories**: Auto-populated from Specific Policies selection

- **Headers**: Auto-populated from Specific Policies selection

- **Category Intent**: Auto-populated from Specific Policies selection

## Policy Categorization

### Understanding the Hierarchy

The Policy Categories table provides a structured hierarchy:

1.  **Categories**: Main topics (Abortion, Contraception, etc.)

2.  **Subcategories**: Second-level grouping (Abortion bans, Protecting
    access, etc.)

3.  **Headers**: Third-level grouping (Total ban, Gestational duration
    ban, etc.)

4.  **Specific Policies**: Detailed policy descriptions (24wk or
    viability ban, Fetal personhood, etc.)

### Categorization Process

1.  Open bill record in Bills table

2.  Click in \"Specific Policies\" field (the record link field)

3.  Search for or select appropriate policies from dropdown

4.  Multiple policies can be selected for bills covering multiple topics

5.  Once selected, related fields auto-populate:

    - Policy Categories

    - Subcategories

    - Headers

    - Category Intent

### Best Practices

- **Be specific**: Select the most precise policy that applies

- **Use multiple selections**: Bills often address multiple policies

- **Check intent alignment**: Ensure the auto-populated Category Intent
  matches your Intent selection

- **Consult colleagues**: Ask Kimya for complex legal categorizations

### Example Categorization

For a bill banning abortion after 24 weeks:

- **Specific Policies**: \"24wk or viability ban\"

- **Auto-populated fields**:

  - Categories: \"Abortion\"

  - Subcategories: \"Abortion bans\"

  - Headers: \"Gestational duration ban at or after 18 weeks\"

  - Category Intent: \"Abortion Restrictive\"

  - \"Restrictive\"

## Website Content Preparation

### When to Write Website Blurbs

Website blurbs are required for:

- Bills with status \"Enacted\"

- Bills with status \"Vetoed\"

- Bills requiring immediate public communication

### Writing Website Blurbs

1.  Navigate to Bills table

2.  Filter for enacted/vetoed bills without website blurbs

3.  Write clear, factual description in \"Website Blurb\" field

4.  Include:

    - What the bill does

    - Key policy changes

    - Effective date (if known)

    - Impact on residents

### Website Blurb Examples

**Good example**: \"In April, Gov. Kay Ivey (R) signed legislation (S
102) that provides presumptive Medicaid eligibility for coverage of
prenatal care for pregnant people. The law is scheduled to go into
effect in October.\"

## Exporting Data

### Website Export Process

1.  Navigate to Automations or Extensions tab

2.  Run \"Website Export\" script

3.  Script automatically:

    - Finds all bills marked \"Ready for Website\"

    - Transforms data into website format

    - Creates records in Website Exports table

    - Maps Specific Policies to Subpolicy1-10 fields

    - Sets Positive/Neutral/Restrictive flags based on Intent

4.  Review export results in Website Exports table

5.  Download CSV from Website Exports table

6.  Provide CSV to website team

### What Gets Exported

The website export includes:

- **Bill identification**: State, BillType, BillNumber

- **Content**: WebsiteBlurb

- **Dates**: All relevant action dates

- **Policy tags**: Up to 10 subpolicies from Specific Policies field

- **Intent flags**: Positive/Neutral/Restrictive based on Intent field

- **Special flags**: Ballot Initiative, Court Case (based on Action
  Type)

### Export Validation

The script automatically validates:

- Required fields are present

- Dates are properly formatted

- Category mappings are correct

- Export format matches website requirements

## Common Searches & Reports

### Creating Custom Searches

**To find all medication abortion bills:**

1.  Add filter: Specific Policies contains \"medication abortion\"

2.  Group by State or Current Bill Status

**To find all bills passed in a specific state:**

1.  Add filter: State = \[specific state\]

2.  Add filter: Current Bill Status contains \"Passed\"

3.  Sort by Last Action Date

**To generate end-of-year counts:**

1.  Filter by Introduction Date (year range)

2.  Group by Policy Categories

3.  Use summary to count records in each category

## Automations & Scripts

### Key Automations

**\"Process StateNet Import\":**

- **Trigger**: When record created in StateNet Raw Import

- **Action**: Creates or updates corresponding Bills record

- **Maps**: Summary→Description, Last Status Date→History

- **Links**: Raw Import record to Bills record

**Date Extraction Automations:**

- Extract Introduction Date from History field

- Extract Enacted Date from History field

- Extract Last Action Date from History field

- Update corresponding date fields in Bills table

**Category Population:**

- When Specific Policies selected, auto-populate Policy Categories,
  Subcategories, Headers, Category Intent

### Website Export Script

Located in GitHub repository, the website export script:

1.  Transforms data to match website team\'s expected format

2.  Creates formatted records in Website Exports table

3.  Validates data quality before export

4.  Provides detailed export summary

### Running the Website Export Script

1.  In Airtable, go to Extensions tab

2.  Find and run \"Website Export v2\" script

3.  Review console output for any errors

4.  Check Website Exports table for new records

5.  Download CSV when ready

## Troubleshooting

### Common Issues

**Import Problems:**

- **Issue**: Bills not appearing in Bills table after import

- **Solution**: Check that automation is enabled; verify StateNet Bill
  ID format matches existing records

**Missing Dates:**

- **Issue**: Introduction Date or Enacted Date not populating

- **Solution**: Check History field format; dates must follow
  \"MM/DD/YYYY (Chamber) Action\" pattern

**Category Issues:**

- **Issue**: Categories not auto-populating when Specific Policies
  selected

- **Solution**: Check that Policy Categories record exists and is
  properly linked

**Export Problems:**

- **Issue**: Website export script fails

- **Solution**: Verify all bills have Website Blurb filled; check for
  any required fields that are empty

**Status Discrepancies:**

- **Issue**: Current Bill Status doesn\'t match latest action

- **Solution**: Review History field for proper formatting; check that
  latest action is at top of history

### Data Validation

The system includes several validation checks:

- **Date Validation**: Flags future dates or impossible date
  combinations

- **Required Field Checks**: Ensures critical fields are populated
  before export

- **Category Consistency**: Verifies Intent matches Category Intent

### Best Practices

1.  **Regular Imports**: Process StateNet data weekly

2.  **Consistent Categorization**: Use existing Policy Categories
    whenever possible

3.  **Complete Information**: Fill all required fields before marking
    bills complete

4.  **Quality Review**: Double-check website blurbs before marking ready
    for export

5.  **Date Validation**: Check Date Validation field for any warning
    flags (🚫)

6.  **Formula Fields**: Don\'t edit formula fields directly - they
    update automatically

7.  **Backup**: Export important data regularly for backup purposes

## Additional Resources

### External Documentation

- **Airtable Formulas Guide**: [[Detailed explanation of all formula
  fields]{.underline}](https://docs.google.com/document/d/1Vb_WtMppKcPReczRtxCA43uDJsmPzNZJJzOSJ_HVLSQ/edit?usp=share_link)

- **Data Dictionary**: [[Complete field reference
  guide]{.underline}](https://docs.google.com/document/d/1v6_5XuY1ZnUfnZghHAk5UotyNmzmFdCmCB6YTDh1Ud0/edit?usp=share_link)

- **GitHub Repository**: [[Technical documentation and
  scripts]{.underline}](https://github.com/Frydafly/guttmacher-legislative-tracker)

### Formula Fields

The system uses several hidden formula fields that automatically extract
information from text fields. These formulas are documented in detail in
the Airtable Formulas Guide above, including:

- **Introduction Date Formula**: Searches History and StateNet History
  fields for introduction dates

- **Enacted Date Formula**: Searches for signing or veto override dates

- **Last Action Date Formula**: Finds the most recent action date
  between History fields

- **Date Validation Formula**: Flags any dates set in the future with
  warning emoji

### Getting Help

- **Technical Issues**: Contact Fryda

- **Policy Questions**: Consult Mollie

- **Legal Review**: Consult Kimya

- **Editorial Review**: Consult Candace/Mollie \_\_\_\_

- **Formula Questions**: See Airtable Formulas Guide above

- **Field Definitions**: See Data Dictionary above

- **Script Documentation**: Check GitHub repository

*For additional technical documentation and script details, see the
GitHub repository:
[[https://github.com/Frydafly/guttmacher-legislative-tracker]{.underline}](https://github.com/Frydafly/guttmacher-legislative-tracker)*
