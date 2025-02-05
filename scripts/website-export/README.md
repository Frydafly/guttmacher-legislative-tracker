# State Legislation Tracker: Website Export Formatter

## 📝 Overview

This Airtable script automates the export of legislative bill data for a website tracking state legislation. It transforms raw bill records into a structured format suitable for web publication.

## 🌟 Features

- Automated bill data export
- Dynamic policy category mapping
- Comprehensive export logging
- Error handling and reporting

## 🔧 Prerequisites

- Airtable account
- Two tables in your base:
  1. "Bills" table
  2. "Website Exports" table

## Configuration
### Bills Table Fields
| Field Name | Description | Type |
|-----------|-------------|------|
| BillID | Unique identifier for the bill | Text |
| Access ID | Internal tracking number | Text |
| State | State jurisdiction | Text |
| BillType | Type of bill | Text |
| BillNumber | Specific bill number | Text |
| Description | Full bill description | Long Text |
| Current Bill Status | Current legislative status | Text |
| Bill Status History | Progression of bill status | Text (Comma-Separated) |
| History | Detailed legislative history | Long Text |
| Last Action | Most recent legislative action | Text |
| Introduction Date | Date bill was introduced | Date |
| Enacted Date | Date bill was enacted | Date |
| Passed Legislature Date | Date bill passed legislature | Date |
| Effective Date | Date bill takes effect | Date |
| Action Type | Type of legislative action | Text |
| Intent | Legislative intent | Text |
| Specific Policies | Specific policy details | Text |
| Policy Categories | Bill's policy domains | Text (Comma-Separated) |
| Prefiled | Prefiling status | Checkbox |
| Review Status | Current review stage | Text |
| Internal Notes | Internal commentary | Long Text |
| Website Blurb | Website-ready summary | Long Text |
| Ready for Website | Export eligibility flag | Checkbox |
| Last Website Export | Timestamp of last export | Date |
| Assigned To | Team member assigned | Text |
| Assignment Date | Date of team assignment | Date |

### Website Exports Table Fields
| Field Name | Description | Type |
|-----------|-------------|------|
| Export Date | Timestamp of export | Date/Time |
| Batch ID | Unique export batch identifier | Text |
| Bill Record | Link back to original bill | Linked Record |
| State | State jurisdiction | Text |
| BillType | Type of legislative bill | Text |
| BillNumber | Specific bill number | Text |
| BillDescription | Full bill description | Long Text |
| WebsiteBlurb | Website-ready summary | Long Text |
| LastActionDate | Most recent action date | Date |
| History | Full legislative history | Long Text |
| Exported By | Export source | Text |
| Abortion | Abortion-related indicator | Text (Yes/No) |
| Appropriations | Appropriations indicator | Text (Yes/No) |
| Contraception | Contraception indicator | Text (Yes/No) |
| FamilyPlanning | Family planning indicator | Text (Yes/No) |
| Insurance | Insurance-related indicator | Text (Yes/No) |
| PeriodProducts | Period products indicator | Text (Yes/No) |
| Pregnancy | Pregnancy-related indicator | Text (Yes/No) |
| Refusal | Refusal provisions indicator | Text (Yes/No) |
| SexEd | Sex education indicator | Text (Yes/No) |
| STIs | STI-related indicator | Text (Yes/No) |
| Youth | Youth-related indicator | Text (Yes/No) |
| Introduced | Introduction status | Text (Yes/No) |
| Passed1Chamber | First chamber passage | Text (Yes/No) |
| Passed2Chamber | Second chamber passage | Text (Yes/No) |
| OnGovDesk | Governor's desk status | Text (Yes/No) |
| Enacted | Enactment status | Text (Yes/No) |
| Vetoed | Veto status | Text (Yes/No) |
| Dead | Bill status | Text (Yes/No) |

## 🚀 Export Process

1. Mark bills as "Ready for Website"
2. Run script
3. Bills are automatically:
   - Validated
   - Categorized
   - Exported to Website Exports table
   - Timestamped

## 📊 Categories Mapped

- Abortion
- Crisis Pregnancy Centers
- Family Planning
- Insurance Coverage
- Youth Access
- Period Products
- Pregnancy

## 💡 Configuration Options

Customize mappings in the `CONFIG` object:
- Adjust field names
- Add/modify website categories
- Define proactive intent criteria

## 🔍 Export Summary

Each export generates a detailed markdown report:
- Batch details
- Record statistics
- Category breakdown
- Error logs

## 🛡️ Error Handling

- Validates required fields
- Logs transformation errors
- Prevents incomplete exports

## Script Usage

### Running the Script

1. Open the "Bills" table in Airtable
2. Navigate to the Scripting tab
3. Paste the entire script
4. Click "Run"

### Preparing Bills for Export

- Ensure all required fields are filled
- Check the "Ready for Website" checkbox
- Verify the "Website Blurb" is complete

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## 🐛 Troubleshooting

- Ensure all field names match exactly in the `CONFIG` object
- Verify "Ready for Website" checkbox is set
- Check that "Website Blurb" is not empty
- Review the export summary for any error messages

