# Guttmacher Legislative Tracker

A dual-purpose repository containing:
1. **Airtable automation scripts** for tracking reproductive health and gender-affirming care legislation
2. **BigQuery components** for staging and analyzing historical legislative data

This repository maintains critical scripts that power the Guttmacher Institute's Policy Tracker through Airtable automations, as well as tools for historical data analysis in BigQuery.

## 🎯 Project Overview

The Guttmacher Legislative Tracker monitors thousands of bills across the United States, tracking their progress through state legislatures and analyzing their potential impact on reproductive health policies. The system consists of three core automation scripts that ensure data quality, generate partner communications, and prepare data for public consumption.

### Key Features
- **Automated Health Monitoring**: Weekly data quality checks and scoring
- **Partner Email Reports**: Bi-weekly legislative updates for stakeholders  
- **Website Data Export**: Public-facing data transformation and validation
- **Real-time Bill Tracking**: Monitor status changes across all 50 states
- **Policy Intent Analysis**: Categorize bills as Positive, Neutral, or Restrictive

## 📁 Repository Structure

```
guttmacher-legislative-tracker/
├── README.md                           # This file
├── CLAUDE.md                          # AI assistant guidance
├── airtable-scripts/                  # Airtable automation scripts
│   ├── health-monitoring/             # Weekly health check automation
│   │   ├── README.md                 # Detailed health monitor docs
│   │   └── health-monitoring.js      # Health check implementation
│   ├── partner-email-report/          # Email report automation
│   │   ├── README.md                 # Email report documentation
│   │   └── partner-email-report.js   # Report generation script
│   └── website-export/                # Public data export
│       ├── README.md                 # Export process documentation
│       └── website-export.js         # Export transformation script
└── bigquery/                          # BigQuery data staging components
    ├── README.md                      # BigQuery documentation
    ├── schema/                        # Table definitions
    ├── etl/                          # ETL scripts
    ├── sql/                          # Analysis queries
    └── data-samples/                 # Sample data files
```

## 🚀 Quick Start

### Prerequisites
- Access to the Guttmacher Policy Tracker Airtable base
- Appropriate permissions to view/edit automations
- Basic understanding of JavaScript and Airtable's scripting environment

### Script Deployment

1. **Access Airtable Automation**:
   - Open the Guttmacher Policy Tracker base
   - Navigate to the "Automations" tab
   - Select the relevant automation

2. **Update Script**:
   - Copy the script content from this repository
   - Paste into the script action within the automation
   - Test using Airtable's built-in testing tools

3. **Verify Configuration**:
   - Check that all field names in CONFIG objects match your base
   - Ensure table names are correct
   - Validate any custom settings

## 📊 Core Components

### 1. Health Monitoring Script
Performs comprehensive weekly health checks to ensure data quality and integrity.

**Key Metrics**:
- Data Quality Score (0-100)
- Bills by status and category
- Missing required fields
- Date validation issues
- Week-over-week changes

**Quality Score Calculation**:
- 30% - Required fields completeness
- 30% - Category assignment coverage
- 40% - Website blurb completeness for enacted/vetoed bills

[View detailed documentation →](airtable-scripts/health-monitoring/README.md)

### 2. Partner Email Report Script
Generates bi-weekly legislative update emails for partner organizations.

**Features**:
- Recent legislative actions (past 2 weeks)
- Bills organized by intent (Positive/Restrictive)
- HTML and plain text output formats
- Automated distribution via Airtable

[View detailed documentation →](airtable-scripts/partner-email-report/README.md)

### 3. Website Export Script
Transforms internal tracking data for public website consumption.

**Capabilities**:
- Complete data refresh strategy
- Subpolicy extraction and mapping
- Intent flag generation
- Rich text field handling
- Duplicate detection and removal

[View detailed documentation →](airtable-scripts/website-export/README.md)

## 🗄️ Database Schema

The scripts interact with four primary Airtable tables:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **Bills** | Core legislative tracking | State, BillType, Status, Intent, Dates |
| **StateNet Raw Import** | External data imports | Import batch tracking |
| **System Monitor** | Health check results | Quality scores, metrics, alerts |
| **Website Exports** | Public data staging | Formatted bill data, subpolicies |

## 🔧 Development Workflow

### Local Development
```bash
# Clone the repository
git clone [repository-url]

# Make your changes
# Test logic locally where possible

# Commit changes
git add .
git commit -m "Description of changes"
git push
```

### Testing in Airtable
1. Use the "Test" button in the automation script editor
2. Review console output for errors
3. Verify output in target tables
4. Run a limited test before full deployment

### Best Practices
- Always backup existing scripts before modifications
- Test with production-like data volumes
- Document any field name changes
- Update CONFIG objects when base schema changes
- Use descriptive commit messages

## 🐛 Troubleshooting

### Common Issues

**Script Timeout**
- Scripts have execution time limits
- Break large operations into smaller batches
- Optimize queries and reduce unnecessary operations

**Field Name Mismatches**
- Update CONFIG objects when Airtable fields change
- Check for typos in field references
- Verify field types match expected formats

**Rich Text Fields**
- Use `.text` property for rich text field content
- Handle both string and object return types
- Apply proper sanitization for CSV exports

## 📞 Support & Contact

**Technical Maintenance**: fryda.guedes@proton.me

**Documentation**: This repository serves as the primary documentation source

**Backups**: Additional copies maintained in shared drive under "Policy Tracker/Scripts"

## 🔒 Security & Access

- Scripts run in Airtable's sandboxed environment
- No external API calls or dependencies
- Access controlled through Airtable permissions
- Sensitive data remains within Airtable base

## 📄 License

This project is proprietary to the Guttmacher Institute. All rights reserved.

---

*Last updated: January 2025*