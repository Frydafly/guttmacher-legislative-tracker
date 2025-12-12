# BigQuery for Policy Analysts

A beginner-friendly guide to querying 22 years of historical legislative data using BigQuery.

!!! info "What is BigQuery?"
    BigQuery is Google's cloud data warehouse. Think of it as a massive, super-fast spreadsheet that can handle millions of rows. We use it to store and analyze historical legislative data from 2002-2024.

## Why Use BigQuery?

### What's In There?

**22,459 bills** tracked across **22 years** (2002-2024):
- All historical legislative data from Access databases
- Policy categorizations and outcomes
- Complete status histories
- Geographic and temporal trends

### What Can You Do?

✅ **Historical trend analysis** - How have abortion bills changed over 20 years?
✅ **Cross-state comparisons** - Which states introduced the most restrictive bills?
✅ **Policy area deep dives** - Track contraception legislation evolution
✅ **Outcome rates** - What percentage of bills are enacted by state?
✅ **Custom reports** - Answer specific research questions quickly

### When to Use BigQuery vs. Airtable?

| Task | Use This |
|------|----------|
| Current year tracking | **Airtable** - Real-time, up-to-date |
| Multi-year trends | **BigQuery** - Historical analysis |
| Partner reports | **Airtable** - Current session data |
| Research papers | **BigQuery** - Comprehensive history |
| Quick counts | **Airtable** - Faster for small queries |
| Complex analytics | **BigQuery** - Powerful aggregations |

## Getting Access

### Step 1: Verify You Have Access

1. **Open Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Sign in** with your Guttmacher email
3. **Check project list** - you should see `guttmacher-legislative-tracker`

!!! warning "No Access?"
    Contact Lenny Munitz or Fryda Guedes to request BigQuery access for the project.

### Step 2: Navigate to BigQuery

1. In Cloud Console, click **hamburger menu** (☰) in top left
2. Scroll to **"Big Data"** section
3. Click **"BigQuery"**
4. You should see BigQuery Studio interface

### Step 3: Find the Data

In the left Explorer panel:

```
📁 guttmacher-legislative-tracker (project)
  └── 📊 legislative_tracker_historical (dataset)
      ├── 📄 all_historical_bills_unified (main view)
      ├── 📄 comprehensive_bills_authentic (enhanced view)
      ├── 📄 historical_bills_2002
      ├── 📄 historical_bills_2003
      ├── ...
      └── 📄 historical_bills_2024
```

## Your First Query

Let's count bills by year - copy this into BigQuery:

```sql
SELECT
  year,
  COUNT(*) as total_bills
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY year
ORDER BY year;
```

**Click "Run"** ▶️

You should see results showing bill counts from 2002-2024!

### Understanding the Query

```sql
SELECT                 -- "Show me..."
  year,                -- ...the year
  COUNT(*) as          -- ...count of records
    total_bills        -- ...call it "total_bills"
FROM `...unified`      -- ...from this table
GROUP BY year          -- ...grouped by year
ORDER BY year;         -- ...sorted by year
```

!!! tip "Query Tips"
    - SQL is not case-sensitive: `SELECT` = `select` = `SeLeCt`
    - Table names must be in backticks: `` `project.dataset.table` ``
    - End queries with semicolon: `;`
    - Click "Format" button to auto-indent your query

## Common Queries

### Bills by State (Current Year)

```sql
SELECT
  state,
  COUNT(*) as bill_count
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year = 2024
GROUP BY state
ORDER BY bill_count DESC;
```

### Abortion Bills Over Time

```sql
SELECT
  year,
  COUNTIF(abortion = TRUE) as abortion_bills
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE abortion IS NOT NULL  -- Only years when tracked
GROUP BY year
ORDER BY year;
```

!!! warning "Important: NULL vs FALSE"
    Fields can be:
    - **NULL** = Not tracked that year (field didn't exist)
    - **FALSE** = Tracked but marked as negative
    - **TRUE** = Tracked and marked as positive

    Always filter out NULLs when analyzing specific policies!

### Enacted Bills by State (2020-2024)

```sql
SELECT
  state,
  year,
  COUNT(*) as enacted_count
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE
  enacted = TRUE
  AND year BETWEEN 2020 AND 2024
GROUP BY state, year
ORDER BY state, year;
```

### Restrictive vs Protective Bills

```sql
SELECT
  year,
  COUNTIF(positive = TRUE) as protective,
  COUNTIF(restrictive = TRUE) as restrictive,
  COUNTIF(neutral = TRUE) as neutral
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year >= 2009  -- Intent tracking starts 2009
GROUP BY year
ORDER BY year;
```

## Understanding the Data

### Data Eras

The data collection evolved over time:

| Era | Years | What's Available |
|-----|-------|------------------|
| **Foundation** | 2002-2005 | Basic bills, core policies |
| **Revolution** | 2006-2015 | Modern status tracking begins |
| **Comprehensive** | 2016-2018 | Complete dates added |
| **Modern** | 2019-2024 | Full data, all features |

See [Data Evolution](../historical/data-evolution.md) for details.

### Important Data Gaps

!!! danger "Known Gaps - Filter These Out"
    - **Introduced dates**: Not tracked before 2016 (NULL)
    - **Contraception**: Complete gap 2006-2008 (not tracked)
    - **Status methodology**: Changed in 2006 (not comparable)
    - **Intent "Restrictive"**: Only tracked from 2009+

### Recommended Date Filters

For most reliable analyses:

```sql
-- For complete data analysis
WHERE year >= 2016

-- For status/outcome analysis
WHERE year >= 2006

-- For intent analysis (restrictive)
WHERE year >= 2009

-- For contraception analysis
WHERE year NOT BETWEEN 2006 AND 2008
```

## Which View Should I Use?

### all_historical_bills_unified

**Best for**: Raw data analysis, custom calculations

**Contains**: Simple union of all year tables, no transformations

**Example**:
```sql
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE year = 2024;
```

### comprehensive_bills_authentic

**Best for**: Reports, dashboards, geographic analysis

**Contains**: Same data PLUS helpful calculated fields:
- `state_name` (AL → Alabama)
- `region` (South, Northeast, etc.)
- `data_era` (Foundation, Revolution, etc.)
- `status_summary` (Enacted, Failed/Dead, etc.)
- `policy_area_count`

**Example**:
```sql
SELECT
  state_name,
  region,
  status_summary,
  COUNT(*) as bills
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.comprehensive_bills_authentic`
WHERE year = 2024
GROUP BY state_name, region, status_summary;
```

!!! tip "Performance Tip"
    Both views have materialized table versions for faster queries. Use:
    - `all_historical_bills_materialized` instead of `..._unified`

## Creating Looker Studio Dashboards

### Step 1: Create a Report

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Click **"Create"** → **"Report"**
3. Select **"BigQuery"** as data source

### Step 2: Connect to Data

1. **Project**: `guttmacher-legislative-tracker`
2. **Dataset**: `legislative_tracker_historical`
3. **Table**: `comprehensive_bills_authentic` (recommended for dashboards)
4. Click **"Add"**

### Step 3: Build Your First Chart

**Example: Bills by Year**

1. **Chart type**: Time series or column chart
2. **Dimension**: `year`
3. **Metric**: `Record Count`
4. **Sort**: `year` ascending

### Step 4: Add Filters

**Example filters**:
- Year range: `year >= 2016`
- Specific state: `state = "TX"`
- Policy area: `abortion = true`
- Status: `enacted = true`

### Sample Dashboard Ideas

1. **Geographic Dashboard**
   - Map of bills by state (use `state` field)
   - Regional breakdown (use `region`)
   - Top 10 states by volume

2. **Trend Dashboard**
   - Bills over time (line chart)
   - Enacted vs. failed (stacked area)
   - Policy areas over time (multi-line)

3. **Policy Analysis**
   - Abortion vs. contraception trends
   - Restrictive vs. protective ratios
   - Emerging policy areas (period products, etc.)

## Advanced Queries

### Multi-State Comparison

```sql
SELECT
  state,
  year,
  COUNTIF(abortion = TRUE AND restrictive = TRUE) as restrictive_abortion,
  COUNTIF(abortion = TRUE AND positive = TRUE) as protective_abortion
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.comprehensive_bills_authentic`
WHERE
  state IN ('TX', 'CA', 'NY', 'FL')
  AND year >= 2016
GROUP BY state, year
ORDER BY state, year;
```

### Bills Covering Multiple Policy Areas

```sql
SELECT
  bill_id,
  state,
  year,
  description,
  policy_area_count
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.comprehensive_bills_authentic`
WHERE policy_area_count >= 3  -- Bills covering 3+ areas
ORDER BY policy_area_count DESC, year DESC;
```

### Enactment Rate by State

```sql
WITH state_stats AS (
  SELECT
    state,
    COUNT(*) as total_bills,
    COUNTIF(enacted = TRUE) as enacted_bills
  FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
  WHERE year >= 2016
  GROUP BY state
)
SELECT
  state,
  total_bills,
  enacted_bills,
  ROUND(100.0 * enacted_bills / total_bills, 1) as enactment_rate_pct
FROM state_stats
WHERE total_bills >= 10  -- Only states with 10+ bills
ORDER BY enactment_rate_pct DESC;
```

## Exporting Results

### Download as CSV

1. Run your query
2. Click **"Save Results"** dropdown
3. Select **"CSV (local file)"**
4. Choose location and save

### Export to Google Sheets

1. Run your query
2. Click **"Explore Data"** → **"Explore with Sheets"**
3. New Google Sheet created with results
4. Can refresh data later from sheet

### Export to Another Project

```sql
EXPORT DATA OPTIONS(
  uri='gs://your-bucket/filename-*.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
SELECT * FROM `your-query-here`;
```

## Troubleshooting

### "Permission denied" Error

**Solution**: Contact Lenny or Fryda for project access

### "Table not found" Error

**Check**:
- Project ID correct: `guttmacher-legislative-tracker`
- Dataset name correct: `legislative_tracker_historical`
- Table name correct (use tab-completion!)
- Using backticks around full table path

### Query Returns Unexpected Results

**Common issues**:
- Not filtering out NULL values
- Comparing across methodology change (2006)
- Using wrong time period
- Not accounting for data gaps

See [Data Evolution](../historical/data-evolution.md) for methodology details.

### Query is Slow

**Solutions**:
- Use materialized tables (`..._materialized`)
- Add WHERE clauses to filter early
- Avoid `SELECT *` - specify needed columns
- Use LIMIT for testing: `LIMIT 100`

## Example Analysis Questions

Here are common research questions and how to answer them:

??? example "How many abortion bills were enacted in 2022?"
    ```sql
    SELECT COUNT(*) as enacted_abortion_bills
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
    WHERE
      year = 2022
      AND abortion = TRUE
      AND enacted = TRUE;
    ```

??? example "Which states had the most restrictive bills since 2020?"
    ```sql
    SELECT
      state,
      COUNT(*) as restrictive_bills
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
    WHERE
      year >= 2020
      AND restrictive = TRUE
    GROUP BY state
    ORDER BY restrictive_bills DESC
    LIMIT 10;
    ```

??? example "What percentage of bills are enacted each year?"
    ```sql
    SELECT
      year,
      COUNT(*) as total_bills,
      COUNTIF(enacted = TRUE) as enacted,
      ROUND(100.0 * COUNTIF(enacted = TRUE) / COUNT(*), 1) as enactment_rate
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
    WHERE year >= 2006  -- Modern status tracking
    GROUP BY year
    ORDER BY year;
    ```

??? example "How has contraception legislation trended?"
    ```sql
    SELECT
      year,
      COUNTIF(contraception = TRUE) as total_contraception,
      COUNTIF(contraception = TRUE AND positive = TRUE) as protective,
      COUNTIF(contraception = TRUE AND restrictive = TRUE) as restrictive
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
    WHERE
      year >= 2009  -- Skip 2006-2008 gap
      AND contraception IS NOT NULL
    GROUP BY year
    ORDER BY year;
    ```

## Learning More

### SQL Resources

- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [SQL for Data Analysis (Mode Analytics)](https://mode.com/sql-tutorial/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

### Project-Specific Docs

- [Data Evolution Guide](../historical/data-evolution.md) - Understanding methodology changes
- [BigQuery Migration Report](../historical/bigquery-migration.md) - How data was migrated
- [Data Dictionary](../reference/data-dictionary.md) - Field definitions

## Getting Help

**Data questions**: Check [Data Evolution](../historical/data-evolution.md) first

**SQL questions**: Try [Stack Overflow](https://stackoverflow.com/questions/tagged/google-bigquery) or ask Fryda

**Access issues**: Contact Lenny Munitz or Fryda Guedes

**Policy/categorization questions**: Contact Mollie Fairbanks or Kimya Forouzan

---

**Happy querying!** Start simple, experiment often, and remember: NULL ≠ FALSE! 📊
