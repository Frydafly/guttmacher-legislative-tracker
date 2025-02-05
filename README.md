# Guttmacher Policy Tracker Automations

This repository contains Airtable automation scripts for the Guttmacher Policy Tracking system.

## Scripts

### Status Change Detector
Located in `scripts/status-detector/`, this script automatically detects and flags bills that need review based on:
- Critical status changes (Enacted, Vetoed, Dead)
- Chamber movement
- Significant legislative actions
- Website update needs

### Website Export
Located in `scripts/website-export/`, this script reconfigures the bills marked as ready for export and:
- renames fields
- recategorizes categories
- extracts only needed fields
- exports to a table titled "Website Exports"
- writes the website exported date in the "Bills" table

## Setup

1. Copy the desired script from its directory
2. Create a new Airtable automation
3. Set the trigger (typically time-based)
4. Paste the script into the "Run script" action
5. Update any configuration if needed
6. Test the automation

## Contributing

1. Create a branch for your changes
2. Update the relevant script
3. Test in Airtable
4. Submit a pull request
5. Include test results in the PR description

## Documentation

See the `docs/` directory for detailed setup instructions and configuration guides.
