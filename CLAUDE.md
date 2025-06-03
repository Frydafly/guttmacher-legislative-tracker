# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Guttmacher Legislative Tracker is a collection of JavaScript scripts that run within Airtable's automation platform to monitor and maintain policy tracking data. These scripts track legislative bills across US states related to reproductive health and gender-affirming care.

## Architecture

- **Platform**: Scripts run inside Airtable automations (sandboxed JavaScript environment)
- **No external dependencies**: Scripts cannot use npm packages or external libraries
- **Database**: Airtable base with four main tables: Bills, StateNet Raw Import, System Monitor, Website Exports
- **Deployment**: Scripts are manually copied from this repository into Airtable automation script steps

## Key Scripts

1. **health-monitoring.js**: Weekly automated health checks that calculate data quality scores and identify issues
2. **partner-email-report.js**: Bi-weekly report generator that creates HTML/text emails about recent legislative activity
3. **website-export.js**: Manual export script that transforms bill data for public website consumption

## Development Commands

Since these are Airtable scripts, there are no traditional build/test commands. Instead:

- **Linting**: Use standard JavaScript linting tools locally before copying to Airtable
- **Testing**: Test scripts directly in Airtable's script editor using the "Test" button
- **Deployment**: Copy script contents into corresponding Airtable automation script steps

## Important Technical Details

1. **Airtable API Constraints**: 
   - Scripts use Airtable's built-in objects: `base`, `table`, `output`, `input`
   - No `require()` or `import` statements allowed
   - Limited to Airtable's JavaScript runtime environment

2. **Field Configuration**: Each script has a CONFIG object mapping field names. Update these if Airtable field names change.

3. **Intent Mapping**: Bills can have multiple intents (Positive, Neutral, Restrictive) that get mapped to binary flags in exports.

4. **Data Validation**: Scripts include extensive validation for dates, required fields, and data consistency.

5. **Error Handling**: Scripts use try-catch blocks and generate detailed error reports in the System Monitor table.

## Common Tasks

When modifying scripts:
1. Always preserve the CONFIG object structure at the top of each script
2. Test date parsing and formatting carefully - scripts handle various date formats
3. Maintain backward compatibility with existing Airtable field names
4. Include detailed console output for debugging within Airtable

When adding new features:
1. Check Airtable's scripting API documentation for available methods
2. Consider performance - scripts have execution time limits
3. Update the corresponding README.md in the script's directory
4. Test with production-like data volumes