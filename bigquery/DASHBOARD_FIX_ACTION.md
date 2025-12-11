# What You Need to Do Right Now

## The Problem
Your Looker Studio dashboard has a broken "Data Quality Report" chart that's looking for a view called `tracking_completeness_matrix` that doesn't exist.

## The Solution (Pick One)

### Option 1: Delete the broken chart (30 seconds)
1. Open Looker Studio dashboard
2. Click on "Data Quality Report" chart
3. Delete it
4. Done

**Why this is probably best:** Data quality checking is something you do once in a while, not something you need on a live dashboard. Just run SQL queries in BigQuery Console when you need to check data quality.

### Option 2: Fix the chart to use the view that DOES exist (5 minutes)
1. Open Looker Studio dashboard
2. Click on "Data Quality Report" chart
3. Click "Data" panel on right
4. Change data source from `tracking_completeness_matrix` to `raw_data_tracking_by_year`
5. Rebuild the chart with these fields:
   - Dimension: `data_year`
   - Metrics: `abortion_tracking_pct`, `contraception_tracking_pct`, `incarceration_tracking_pct`
6. Done

## When You Need Data Quality Info

Run this query in BigQuery Console:

```sql
SELECT
  data_year,
  total_bills,
  ROUND(abortion_tracking_pct, 1) as abortion_pct,
  ROUND(contraception_tracking_pct, 1) as contraception_pct,
  ROUND(incarceration_tracking_pct, 1) as incarceration_pct
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.raw_data_tracking_by_year`
ORDER BY data_year DESC
```

## That's It

The views are documented but never existed. Your main data (20,221 bills) is fine. The `comprehensive_bills_authentic` view you're using in other charts is working correctly.

---

**Full details if you want them:** See `LOOKER_DASHBOARD_FIX.md`
**SQL query file:** `sql/data_quality_report.sql`
