# Guttmacher Legislative Tracker Documentation

Welcome to the comprehensive documentation for the **Guttmacher Legislative Tracker** - a multi-purpose system for tracking state-level legislation related to sexual and reproductive health and rights.

## What is This System?

The Guttmacher Legislative Tracker is a sophisticated data pipeline that:

- **Monitors** state legislation across all 50 US states
- **Processes** weekly imports from StateNet data feeds
- **Tracks** policy categorization and legislative outcomes
- **Generates** public-facing website content and partner reports
- **Analyzes** historical trends via BigQuery data warehouse (2002-2024)

## System Components

### Airtable Database
The operational heart of the system - a structured database that processes legislative data through review, categorization, and publication workflows.

[:material-table: User Manual](user-guides/airtable-user-manual.md){ .md-button }
[:material-database: Schema Reference](reference/airtable-schema.md){ .md-button .md-button--primary }

### Automation Scripts
JavaScript scripts running within Airtable that automate data quality monitoring, partner reporting, and website exports.

[:material-robot: View Scripts](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts){ .md-button }
[:material-file-document: Deployment Guide](technical/deployment-guide.md){ .md-button .md-button--primary }

### BigQuery Analytics
Historical data warehouse containing 22 years (2002-2024) of legislative data for trend analysis and reporting.

[:material-chart-line: BigQuery for Analysts](user-guides/bigquery-for-analysts.md){ .md-button }
[:material-history: Migration Report](historical/bigquery-migration.md){ .md-button .md-button--primary }

## Quick Links

!!! tip "For Policy Team Members"
    - [Airtable User Manual](user-guides/airtable-user-manual.md) - Complete guide to daily operations
    - [Data Dictionary](reference/data-dictionary.md) - What each field means
    - [Running Reports](user-guides/running-reports.md) - Generate partner reports

!!! info "For Technical Users"
    - [Deployment Guide](technical/deployment-guide.md) - How to deploy script updates
    - [Runbook](technical/runbook.md) - Troubleshooting common issues
    - [Architecture Overview](getting-started/architecture.md) - System design and data flow

!!! example "For Analysts & Researchers"
    - [BigQuery for Analysts](user-guides/bigquery-for-analysts.md) - Query historical data
    - [Data Evolution](historical/data-evolution.md) - Understanding methodology changes
    - [Airtable Formulas](reference/airtable-formulas.md) - How calculations work

## Recent Updates

**December 2025**: Recovered from data deletion incident using BigQuery backups ([Incident Report](https://github.com/Frydafly/guttmacher-legislative-tracker/blob/main/INCIDENTS.md))

**July 2025**: Successfully migrated 22 years of historical data (22,459 bills) to BigQuery

**June 2025**: Deployed enhanced website export script with quality metrics and pre-flight validation

## Getting Help

- **Policy Questions**: Contact Mollie Fairbanks or Kimya Forouzan
- **Technical Issues**: Contact Fryda Guedes (fryda.guedes@proton.me)
- **Website/IT**: Contact Lenny Munitz

## Project Philosophy

!!! quote "Small Team = Pragmatic Solutions"
    This system follows a **simple > perfect** philosophy. We avoid over-engineering and focus on solutions that work reliably with minimal maintenance burden.

    Before building any new tool, we ask:

    1. How often does this occur? (Rare = manual, Monthly = script, Weekly+ = automate)
    2. Can we solve with existing tools/comments/checklists?
    3. Who maintains this when you're gone?

---

**Ready to get started?** Check out the [Quick Start Guide](getting-started/quick-start.md) or explore the navigation menu above.
