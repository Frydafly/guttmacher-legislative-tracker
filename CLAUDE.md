# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Guttmacher Legislative Tracker is a dual-purpose repository containing:

1. **Airtable automation scripts** that run within Airtable's automation platform to monitor and maintain policy tracking data
2. **BigQuery historical data pipeline** for processing and analyzing historical legislative data from Access databases

## Architecture

### Airtable Scripts (`airtable-scripts/`)
- **Platform**: Scripts run inside Airtable automations (sandboxed JavaScript environment)
- **No external dependencies**: Scripts cannot use npm packages or external libraries
- **Database**: Airtable base with four main tables: Bills, StateNet Raw Import, System Monitor, Website Exports
- **Deployment**: Scripts are manually copied from this repository into Airtable automation script steps

### BigQuery Pipeline (`bigquery/`)
- **Platform**: Python scripts that run locally or in cloud environments
- **Purpose**: Extract, transform, and load historical .mdb files into BigQuery for analytics
- **Output**: Looker Studio-ready views that approximate current Airtable structure
- **Environment**: Uses virtual environment (`venv/`) with dependencies in `requirements.txt`

## Key Scripts

### Airtable Scripts
1. **health-monitoring.js**: Weekly automated health checks that calculate data quality scores and identify issues
2. **partner-email-report.js**: Bi-weekly report generator that creates HTML/text emails about recent legislative activity
3. **website-export.js**: Manual export script that transforms bill data for public website consumption

### BigQuery Pipeline
1. **historical_data_pipeline.py**: Complete ETL pipeline for processing .mdb files
2. **data_transformer.py**: Core transformation logic for standardizing historical data
3. **mdb_to_bigquery_pipeline.py**: Alternative pipeline using mdbtools

## Development Commands

### Airtable Scripts
Since these are Airtable scripts, there are no traditional build/test commands. Instead:
- **Linting**: Use standard JavaScript linting tools locally before copying to Airtable
- **Testing**: Test scripts directly in Airtable's script editor using the "Test" button
- **Deployment**: Copy script contents into corresponding Airtable automation script steps

### BigQuery Pipeline
```bash
# Setup environment
cd bigquery
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Test setup
python etl/test_connection.py

# Run pipeline
python etl/historical_data_pipeline.py
```

## Important Technical Details

### Airtable Constraints
1. **Airtable API Constraints**: 
   - Scripts use Airtable's built-in objects: `base`, `table`, `output`, `input`
   - No `require()` or `import` statements allowed
   - Limited to Airtable's JavaScript runtime environment

2. **Field Configuration**: Each script has a CONFIG object mapping field names. Update these if Airtable field names change.

3. **Intent Mapping**: Bills can have multiple intents (Positive, Neutral, Restrictive) that get mapped to binary flags in exports.

### BigQuery Pipeline Constraints
1. **Environment Management**: 
   - Uses virtual environment (`venv/`) - NOT committed to git
   - All dependencies listed in `requirements.txt`
   - Environment variables in `.env` file (also NOT committed to git)

2. **Data Security**: 
   - Historical .mdb files are NOT committed to git
   - All processing happens within user's Google Cloud project
   - Generated CSV and processed files are excluded from git

3. **Schema Mapping**: 
   - Configuration in `schema/field_mappings.yaml` controls how historical fields map to current structure
   - Handles inconsistent naming, date formats, and data types across years

## Common Tasks

### When modifying Airtable scripts:
1. Always preserve the CONFIG object structure at the top of each script
2. Test date parsing and formatting carefully - scripts handle various date formats
3. Maintain backward compatibility with existing Airtable field names
4. Include detailed console output for debugging within Airtable

### When modifying BigQuery pipeline:
1. Always activate virtual environment first: `source venv/bin/activate`
2. Update `schema/field_mappings.yaml` when adding new field mappings
3. Test with `test_connection.py` before running full pipeline
4. Check logs for data quality issues and mapping problems
5. Update requirements.txt if adding new dependencies

### When adding new features:
1. **Airtable**: Check Airtable's scripting API documentation for available methods
2. **BigQuery**: Consider performance - large datasets require proper optimization
3. Update the corresponding README.md in the script's directory
4. Test with production-like data volumes

## File Structure Notes

```
guttmacher-legislative-tracker/
├── airtable-scripts/           # Airtable automation scripts
│   ├── health-monitoring/
│   ├── partner-email-report/
│   └── website-export/
├── bigquery/                   # BigQuery historical data pipeline
│   ├── venv/                  # Virtual environment (NOT in git)
│   ├── .env                   # Environment config (NOT in git)
│   ├── data/historical/       # .mdb files (NOT in git)
│   ├── schema/               # Field mappings and configurations
│   ├── etl/                  # ETL pipeline scripts
│   ├── sql/                  # BigQuery views and queries
│   └── requirements.txt      # Python dependencies
├── CLAUDE.md                  # This file
└── README.md                 # Main project documentation
```

## Git and Security Best Practices

### What IS committed:
- Source code and pipeline scripts
- Configuration templates (`.env.example`)
- Documentation and setup guides
- Requirements files for reproducible environments

### What is NOT committed:
- Virtual environments (`venv/`, `.venv/`)
- Environment variables (`.env`)
- Database files (`.mdb`, `.accdb`)
- Generated data (`.csv`, processed files)
- Log files and temporary data

### Important Reminders:
- Never commit sensitive data or credentials
- Always use virtual environments for Python development
- Keep documentation updated when making changes
- Test both Airtable scripts and BigQuery pipeline changes thoroughly
- Consider data privacy when working with historical legislative data

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.