# Quick Start Guide

Get up and running with the Guttmacher Legislative Tracker in minutes.

## For Policy Team Members

### Your Daily Workflow

1. **Check for new imports** in StateNet Raw Import table
2. **Review new bills** flagged as "Needs Review" in Bills table
3. **Categorize bills** using Specific Policies field
4. **Write blurbs** for enacted/vetoed legislation
5. **Mark complete** when review finished

**→ [Full User Manual](../user-guides/airtable-user-manual.md)**

### Essential Links

- **Airtable Base**: [Link shared via email]
- **Data Dictionary**: [Field definitions](../reference/data-dictionary.md)
- **Formulas Guide**: [How calculations work](../reference/airtable-formulas.md)

---

## For Analysts & Researchers

### Querying Historical Data

**Step 1**: Access BigQuery
```
console.cloud.google.com → BigQuery → legislative_tracker_historical
```

**Step 2**: Run your first query
```sql
SELECT year, COUNT(*) as bills
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY year
ORDER BY year;
```

**Step 3**: Learn more queries
**→ [BigQuery for Analysts Guide](../user-guides/bigquery-for-analysts.md)**

### Creating Dashboards

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Create report → BigQuery data source
3. Select `comprehensive_bills_authentic` view
4. Build visualizations

**→ [Dashboard Examples](../user-guides/bigquery-for-analysts.md#creating-looker-studio-dashboards)**

---

## For Developers & Technical Users

### Deploying Scripts

**Pre-flight checklist**:
- [ ] Code reviewed and tested
- [ ] Changes committed to GitHub
- [ ] Current production script backed up
- [ ] CONFIG object verified

**Deploy**:
1. Copy script from GitHub
2. Paste into Airtable automation
3. Test run
4. Monitor for 24 hours

**→ [Full Deployment Guide](../technical/deployment-guide.md)**

### Repository Structure

```
guttmacher-legislative-tracker/
├── airtable-scripts/          # Automation scripts
│   ├── health-monitoring/
│   ├── partner-email-report/
│   └── website-export/
├── bigquery/                  # Historical data pipeline
│   ├── etl/                  # ETL scripts
│   ├── schema/               # Field mappings
│   └── sql/                  # BigQuery views
└── docs/                     # This documentation (MkDocs)
```

**→ [Architecture Overview](architecture.md)**

---

## For Web Team

### Getting Website Export Data

**Process**:
1. Policy team runs Website Export script in Airtable
2. Exports to "Website Exports" table
3. Download as CSV
4. Receives via Asana or email

**Format**: CSV with fields mapped to website requirements

**→ Contact**: Policy team

---

## Common Tasks

### "I need to import StateNet data"

1. Download CSV from StateNet
2. Open Airtable → StateNet Raw Import table
3. Click "+" to add records or import CSV
4. Map fields:
   - StateNet Bill ID → StateNet Bill ID
   - Jurisdiction → Jurisdiction
   - Summary → Summary
   - Last Status Date → Last Status Date
5. Automation will process automatically

**→ [Detailed Instructions](../user-guides/airtable-user-manual.md#importing-statenet-data)**

---

### "I need to fix a script error"

1. **Check automation run history** in Airtable
2. **Identify error message**
3. **Look up in Runbook**:
   - Field name mismatches
   - Timeout errors
   - Data validation failures

**→ [Runbook](../technical/runbook.md)**

---

### "I need to query historical data"

1. **Access BigQuery** at console.cloud.google.com
2. **Navigate to** `legislative_tracker_historical` dataset
3. **Use** `comprehensive_bills_authentic` view for dashboards
4. **Filter** appropriately:
   - `WHERE year >= 2016` for complete data
   - `WHERE year >= 2006` for modern status tracking

**→ [BigQuery Guide](../user-guides/bigquery-for-analysts.md)**

---

### "I need to generate a partner report"

**Automated**: Runs automatically on 1st and 15th of month

**Manual run**:
1. Airtable → Automations
2. Find "Partner Email Report"
3. Click "Run now"
4. Check output

**→ [Report Details](../user-guides/running-reports.md)**

---

### "I need to understand a field"

**Look up in**:
- [Data Dictionary](../reference/data-dictionary.md) - All field definitions
- [Airtable Schema](../reference/airtable-schema.md) - Table structures
- [Formulas Guide](../reference/airtable-formulas.md) - How calculations work

---

### "Something is broken"

**Step 1**: Check if it's a known issue
- [Runbook](../technical/runbook.md) - Common issues & solutions
- GitHub Issues - Known bugs

**Step 2**: Contact appropriate team
- **Technical issues**: Technical team
- **Policy questions**: Policy team
- **IT/Website**: Web/IT team

---

## Getting Help

!!! question "Can't find what you need?"
    - Check the [Runbook](../technical/runbook.md) for troubleshooting
    - Browse the [full documentation](../index.md)
    - Contact the team (see [contacts](../index.md#getting-help))

---

**Next steps**: Explore the [Architecture](architecture.md) to understand how everything connects.
