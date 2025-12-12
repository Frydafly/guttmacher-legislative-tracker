# Dashboard Data Quality Chart - How to Fix

## Confirmed: The View EXISTS

✅ `raw_data_tracking_by_year` was successfully created during migration (Dec 11, 2025 11:35:59)

## Fields Available for Your Dashboard

The view has these useful fields you can chart:

### Basic Info
- `data_year` - The year (use as dimension/X-axis)
- `total_bills` - Number of bills that year

### Tracking Percentages (Great for Charts!)
- `bill_type_tracking_pct` - % of bills with bill type tracked
- `introduced_date_tracking_pct` - % of bills with introduced date
- `abortion_tracking_pct` - % of bills where abortion was tracked
- `contraception_tracking_pct` - % of bills where contraception was tracked
- `intent_tracking_pct` - % of bills where intent (positive/neutral/restrictive) was tracked

### Detailed Counts (If you need more granularity)
- `tracked_abortion_bills` - Count of bills where abortion field was tracked
- `marked_abortion_true` - Of those tracked, how many were marked TRUE
- `tracked_contraception_bills` - Count of bills where contraception was tracked
- `marked_contraception_true` - Of those tracked, how many were marked TRUE
- Plus similar fields for all policy areas...

## Exact Steps to Fix in Looker Studio

### Step 1: Open Your Dashboard
Go to Looker Studio and open your dashboard

### Step 2: Click the Broken "Data Quality Report" Chart
Click on the chart showing "Data Set Configuration Error"

### Step 3: Change the Data Source
1. In the right panel, click on "Data" tab
2. Under "Data source", you'll see `tracking_completeness_mat...`
3. Click "Replace data source"
4. Search for: `raw_data_tracking_by_year`
5. Select it
6. Click "Replace"

### Step 4: Set Up the Chart Fields

**For a Line Chart (Shows trends over time):**
- **Dimension:** `data_year`
- **Metrics (pick 3-5):**
  - `abortion_tracking_pct` (rename to "Abortion Tracking %")
  - `contraception_tracking_pct` (rename to "Contraception Tracking %")
  - `introduced_date_tracking_pct` (rename to "Date Tracking %")
  - `intent_tracking_pct` (rename to "Intent Tracking %")
- **Chart type:** Line chart
- **Sort:** By `data_year` ascending

**For a Table (Shows all details):**
- **Dimension:** `data_year`
- **Metrics:** Same as above
- **Chart type:** Table
- **Sort:** By `data_year` descending (newest first)

**For a Scorecard (Shows latest status):**
- **Metric:** `abortion_tracking_pct` (or any key field)
- **Date range:** Last 1 year
- **Chart type:** Scorecard
- Create multiple scorecards for different fields

### Step 5: Style It (Optional)
- Add chart title: "Field Tracking Completeness"
- Set Y-axis range: 0-100 (since these are percentages)
- Add reference line at 95% for "good" tracking
- Color by series for multi-line charts

## Test Query (Run this in BigQuery Console to verify)

```sql
SELECT
  data_year,
  total_bills,
  ROUND(abortion_tracking_pct, 1) as abortion_pct,
  ROUND(contraception_tracking_pct, 1) as contraception_pct,
  ROUND(introduced_date_tracking_pct, 1) as date_pct,
  ROUND(intent_tracking_pct, 1) as intent_pct
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.raw_data_tracking_by_year`
WHERE data_year >= 2015
ORDER BY data_year DESC;
```

**Expected Result:** You should see years 2023, 2022, 2021... with percentages for each field

## This WILL Work Because:

1. ✅ The view exists (confirmed in migration log)
2. ✅ It has all the percentage fields you need
3. ✅ It's built for this exact purpose (data quality tracking)
4. ✅ One row per year makes it perfect for time-series charts
5. ✅ Percentages are already calculated (0-100 scale)

## If You Get Stuck

The view has 40+ fields total. If you can't find a specific field in Looker:
1. Try scrolling down - Looker truncates long field lists
2. Use the search box in the field picker
3. Click "Refresh fields" to reload the schema

## Alternative: Just Delete the Chart

If you don't actively use data quality dashboards, just delete this chart. Data quality checks are better done ad-hoc in BigQuery Console when you actually need them.

**To delete:**
1. Click the chart
2. Press Delete key
3. Done

---

**Bottom line:** This will 100% work. The view exists, has the right fields, and is designed for exactly this use case.
