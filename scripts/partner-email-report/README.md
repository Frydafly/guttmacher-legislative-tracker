# Partner Email Report Automation

This script is designed to run as an Airtable automation to generate bi-weekly legislative update emails. It processes records from a "Partner Email Report" view, formats them according to our standard template, and prepares both plain text and HTML email outputs.

## Purpose

The script automatically identifies bills that have passed a chamber or been enacted, organizes them by their intent (Positive or Restrictive), and formats them for a standardized email report to partners.

## How It Works

1. Fetches records from the "Partner Email Report" view in the Bills table
2. Identifies bills with legislative actions in the past two weeks by checking:
   - Enacted Date
   - Vetoed Date
   - Passed Legislature Date
   - Passed First Chamber Date
3. Organizes bills by their intent (Positive or Restrictive)
4. Generates formatted email content with the bill ID, action, date, and description
5. Creates both plain text and HTML email formats

## Required Fields

The script requires the following fields in your Bills table:

- `State` (Single Select)
- `BillType` (Single Select)
- `BillNumber` (Number)
- `Passed 1 Chamber Date` (Date)
- `Passed Legislature Date` (Date)
- `Enacted Date` (Date)
- `Vetoed Date` (Date)
- `Website Blurb` or `Description` (Rich Text)
- `Intent` (Multiple Lookup Values)


## Usage

This script is intended to be used as part of an Airtable automation:

1. Create a new automation with a scheduled trigger (every two weeks)
2. Add a "Run script" action and paste this script
3. Add a "Send email" action that uses the output variables:
   - For HTML emails: `{{formattedHtmlEmail}}`
   - For plain text: `{{formattedEmailBody}}`

## Example Output

The generated email follows this format:

```plaintext
*Positive*

VA H 1649 passed the first chamber on 01/28/2025.
Requires unconscious bias and cultural competency training for physicians...

MS S 2874 passed the first chamber on 02/05/2025.
Requires providers to screen postpartum patients for mental health conditions...

*Restrictive*

AR H 1180 passed the first chamber on 02/06/2025.
Requires the "Baby Olivia" video produced by anti-abortion group...

KS S 63 passed the legislature on 01/31/2025.
Bans gender-affirming care for people younger than 18...
```

In the HTML version, the first line of each bill entry is underlined.

## Maintenance

If field names or formats change in your Airtable base, you may need to update the corresponding references in this script.

## Troubleshooting

If the script doesn't generate the expected output:

1. Check that your "Partner Email Report" view contains the correct records
2. Verify that records have the required field values (especially Status and Intent)
3. Review the automation run logs for any error messages or unexpected values

## Dependencies

This script relies on Airtable's Automation platform APIs and doesn't require external libraries.