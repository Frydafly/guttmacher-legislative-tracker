# Running Reports

Guide to generating various reports from the legislative tracker.

## Automated Reports

### Partner Email Report (Bi-weekly)

**Schedule**: Automatically runs on the 1st and 15th of each month

**Recipients**:
- SiX (full report - all policy areas)
- ACN/NAF (abortion-only report)
- Other partners as needed

**Content**: Recently enacted and vetoed bills with website blurbs

**Format**: HTML email + plain text version

**Manual Run**:
1. Open Airtable
2. Go to Automations tab
3. Find "Partner Email Report"
4. Click "Run now"
5. Check console output for success/errors

**→ See**: [Partner Email Report README](https://github.com/Frydafly/guttmacher-legislative-tracker/tree/main/airtable-scripts/partner-email-report)

---

## Manual Reports from Airtable

### Current Session Bill Counts

**To get bill counts by state**:

1. Open Bills table
2. Apply filter: `Year = 2025` (or current year)
3. Group by: `State`
4. View count summary at bottom

**To export**:
1. Select all records (or filtered view)
2. Click "..." menu → Download CSV
3. Open in Excel/Google Sheets

---

### Bills by Status

**To see all enacted bills**:

1. Create view filter:
   - `Current Bill Status = "Enacted"`
   - `Year = 2025`
2. Group by `State` or `Policy Categories`
3. Export as CSV if needed

**Common status queries**:
- Enacted: `Current Bill Status = "Enacted"`
- Failed: `Current Bill Status = "Dead"`
- Pending: `Current Bill Status = "Passed First Chamber"` or `"Passed Both Chambers"`

---

### Bills by Policy Area

**Example: All abortion bills**:

1. Filter: `Specific Policies contains "abortion"`
2. Group by: `State` or `Intent`
3. Sort by: `Last Action` (most recent first)

**Example: Restrictive bills only**:

1. Filter: `Intent = "Restrictive"`
2. Filter: `Year = 2025`
3. Group by: `Policy Categories`

---

## Reports from BigQuery

For historical analysis and multi-year trends, use BigQuery.

### Annual Bill Counts

```sql
SELECT
  year,
  COUNT(*) as total_bills,
  COUNTIF(enacted = TRUE) as enacted,
  COUNTIF(restrictive = TRUE) as restrictive,
  COUNTIF(positive = TRUE) as protective
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year >= 2006  -- Modern status tracking
GROUP BY year
ORDER BY year;
```

### State Rankings

```sql
SELECT
  state,
  COUNT(*) as total_bills,
  COUNTIF(enacted = TRUE) as enacted,
  ROUND(100.0 * COUNTIF(enacted = TRUE) / COUNT(*), 1) as enactment_rate
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year BETWEEN 2020 AND 2024
GROUP BY state
ORDER BY total_bills DESC;
```

**→ More queries**: [BigQuery for Analysts](bigquery-for-analysts.md)

---

## Custom Dashboards

### Creating Looker Studio Reports

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Create → Report
3. Add data source: BigQuery
   - Project: `guttmacher-legislative-tracker`
   - Dataset: `legislative_tracker_historical`
   - Table: `comprehensive_bills_authentic`
4. Drag and drop visualizations

**Example dashboards**:
- Geographic heat map by state
- Time series of bills over years
- Policy area breakdown (pie chart)
- Enacted vs. failed trends (stacked area)

**→ Detailed guide**: [BigQuery for Analysts - Dashboards](bigquery-for-analysts.md#creating-looker-studio-dashboards)

---

## Report Templates

### End-of-Year Summary

**Airtable approach**:
1. Filter Bills: `Year = 2025`
2. Create multiple views:
   - By State
   - By Status
   - By Policy Area
3. Export each as CSV
4. Combine in Excel/Sheets

**BigQuery approach**:
```sql
SELECT
  state,
  COUNTIF(abortion = TRUE) as abortion,
  COUNTIF(contraception = TRUE) as contraception,
  COUNTIF(insurance = TRUE) as insurance,
  COUNTIF(enacted = TRUE) as enacted
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year = 2024
GROUP BY state;
```

---

### Mid-Session Progress Report

**Track bills introduced vs. enacted so far**:

```sql
SELECT
  state,
  COUNTIF(introduced_date IS NOT NULL) as introduced,
  COUNTIF(enacted = TRUE) as enacted,
  COUNTIF(dead = TRUE) as failed,
  COUNTIF(pending = TRUE) as still_pending
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year = 2025
GROUP BY state;
```

---

## Troubleshooting

### Report Shows No Data

**Check**:
- Filter criteria (year, status, etc.)
- Field names (case-sensitive)
- Permission to access data

### Partner Email Failed to Send

**See**: [Runbook - Partner Email Issues](../technical/runbook.md#issue-partner-email-report-script-failed)

### BigQuery Query Errors

**See**: [BigQuery Troubleshooting](bigquery-for-analysts.md#troubleshooting)

---

## Getting Help

- **Report formatting questions**: Contact Mollie Fairbanks
- **Data questions**: See [Data Dictionary](../reference/data-dictionary.md)
- **BigQuery help**: See [BigQuery Guide](bigquery-for-analysts.md)
- **Technical issues**: Contact Fryda Guedes
