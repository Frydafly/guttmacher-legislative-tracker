# Looker Studio Dashboard Fix Guide

## Problem

Your "Data Quality Report" chart shows a "Data Set Configuration Error" because it's trying to use `tracking_completeness_matrix`, a view that was documented but never actually created.

## Solution Options

### Option 1: Remove the Broken Chart (FASTEST - 2 minutes)

**When to use:** If data quality reports aren't actively used in dashboards

**Steps:**
1. Open your Looker Studio dashboard
2. Click on the "Data Quality Report" chart showing the error
3. Press Delete or click the trash icon
4. Done!

**Pros:**
- Immediate fix
- Data quality analysis should be done via BigQuery Console anyway (more flexible)
- Keeps dashboard focused on user-facing bill analysis

**Cons:**
- Removes the chart entirely

---

### Option 2: Update Chart to Use Existing View (RECOMMENDED - 5 minutes)

**When to use:** If you want to keep a data quality visualization in the dashboard

**Steps:**

1. **Open Looker Studio and select the broken chart**
   - Click on "Data Quality Report" chart

2. **Change the data source:**
   - Click "Data" in the right panel
   - Under "Data source", click the dropdown showing `tracking_completeness_mat...`
   - Click "Replace data source"

3. **Select the correct data source:**
   - Search for: `raw_data_tracking_by_year`
   - Select it and click "Apply"

4. **Rebuild the chart fields:**
   Since the old view doesn't exist, you'll need to reconfigure. Try this simple setup:

   **Dimension (X-axis):**
   - `data_year`

   **Metrics (Y-axis):**
   - `abortion_tracking_pct` (rename to "Abortion Tracking %")
   - `contraception_tracking_pct` (rename to "Contraception Tracking %")
   - `period_products_tracking_pct` (rename to "Period Products Tracking %")
   - `incarceration_tracking_pct` (rename to "Incarceration Tracking %")

   **Chart type suggestions:**
   - Line chart: Shows tracking evolution over time
   - Table: Shows detailed percentages by year
   - Scorecard: Shows latest year's tracking completeness

5. **Optional: Add visual indicators with calculated fields**

   To add emoji indicators like ✅/⚠️/❌:

   **Create calculated field "Abortion Status":**
   ```
   CASE
     WHEN abortion_tracking_pct >= 95 THEN "✅ Complete"
     WHEN abortion_tracking_pct >= 50 THEN "⚠️ Partial"
     WHEN abortion_tracking_pct >= 1 THEN "🔶 Minimal"
     ELSE "❌ Not tracked"
   END
   ```

   Repeat for other key fields (contraception, incarceration, etc.)

**Pros:**
- Keeps data quality visualization in dashboard
- Uses existing, working view
- Can customize to your needs

**Cons:**
- Requires rebuilding the chart configuration

---

### Option 3: Create Custom BigQuery SQL Chart (ADVANCED - 10 minutes)

**When to use:** If you want the exact format from the old documentation

**Steps:**

1. In Looker Studio, add a new chart

2. Click "Add Data" → "BigQuery" → "Custom Query"

3. Select project: `guttmacher-legislative-tracker`

4. Paste the query from `/bigquery/sql/data_quality_report.sql` or use this simplified version:

```sql
SELECT
  data_year,
  total_bills,
  ROUND(abortion_tracking_pct, 1) as abortion_pct,
  ROUND(contraception_tracking_pct, 1) as contraception_pct,
  ROUND(period_products_tracking_pct, 1) as period_products_pct,

  CASE
    WHEN abortion_tracking_pct >= 95 THEN '✅ Complete'
    WHEN abortion_tracking_pct >= 50 THEN '⚠️ Partial'
    ELSE '❌ Not tracked'
  END as abortion_status,

  CASE
    WHEN contraception_tracking_pct >= 95 THEN '✅ Complete'
    WHEN contraception_tracking_pct >= 50 THEN '⚠️ Partial'
    ELSE '❌ Not tracked'
  END as contraception_status

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.raw_data_tracking_by_year`
ORDER BY data_year DESC
```

5. Configure chart with the query results

**Pros:**
- Full control over the data format
- Can include emoji indicators directly
- Can filter/aggregate as needed

**Cons:**
- Custom query runs on each dashboard load (slower)
- More complex to maintain

---

## What About the Missing `comprehensive_bills_authentic` Fields?

Based on your screenshot, charts using `comprehensive_bills_authen...` (abbreviated) appear to be working. This view exists and has all the fields you need:

**Available fields in `comprehensive_bills_authentic`:**
- Core: id, state, bill_number, bill_type, description
- Geographic: state_code, state_name, region
- Dates: introduced_date, enacted_date, last_action_date, etc.
- Status: status_category (Enacted, Vetoed, Dead, Pending, etc.)
- Intent: intent (Positive, Restrictive, Neutral, Unclassified)
- Policy areas: abortion, contraception, minors, insurance, etc.
- Calculated: days_to_enactment, policy_area_count, policy_complexity

If specific fields appear to be missing, it may be a display name issue in Looker. Check:
1. Scroll through the full field list (Looker truncates long lists)
2. Try searching for the field name
3. Refresh the data source schema

---

## Recommended Action

**For most users: Option 1 (Remove chart)**

Data quality reports are better done ad-hoc in BigQuery Console where you can:
- Run custom queries as needed
- Export results for reports
- Investigate specific data issues flexibly

**If you frequently review data quality: Option 2 (Update to existing view)**

This keeps a live dashboard visualization without the maintenance burden of custom SQL queries.

---

## Additional Resources

- **SQL Query for ad-hoc analysis:** `/bigquery/sql/data_quality_report.sql`
- **View documentation:** `/bigquery/2002_2024_Historical_Migration.md`
- **Recovery guide:** `/bigquery/QUICK_RECOVERY.md`

---

## Questions?

If you're unsure which option to choose:
- How often do you look at data quality reports? (Monthly+ → Option 2, Rarely → Option 1)
- Is this for end users or just admins? (End users → Option 2, Admins → Option 1)
- Do you need visual indicators like ✅/⚠️? (Yes → Option 3, No → Option 2)
