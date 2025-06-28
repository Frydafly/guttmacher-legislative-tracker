# Looker Studio Quick Start Guide

## Available Views in BigQuery

You now have the following views ready for Looker Studio:

### Primary Views:
1. **`looker_comprehensive_bills`** - Main comprehensive table with all enhanced fields
   - Best for detailed dashboards with all bill information
   - Includes calculated fields, regions, time periods, status categories
   
2. **`looker_bills_dashboard`** - Streamlined view for dashboards
   - Core bill information with status and intent
   - All policy areas and topics included

3. **`looker_state_summary`** - Pre-aggregated state-level metrics
   - Bills by state and year with counts by type
   - Enactment rates calculated

4. **`looker_time_series`** - Time-based analysis view
   - Monthly and quarterly breakdowns
   - Perfect for trend charts

5. **`looker_topic_analysis`** - Topic-focused analysis
   - Bills grouped by topic with state counts
   - Enactment success by topic

## Quick Start Steps

### 1. Connect to Looker Studio
1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. Create → Report → Add data → BigQuery
3. Select: `guttmacher-legislative-tracker` → `legislative_tracker_historical`
4. Choose your view (start with `looker_comprehensive_bills`)

### 2. Essential Charts to Create

#### Executive Summary (using `looker_comprehensive_bills`):
- **Scorecard**: Total bills (COUNT of id)
- **Pie Chart**: Bills by Intent
- **Time Series**: Bills by year (data_year)
- **Geo Map**: Bills by state_name

#### State Analysis (using `looker_state_summary`):
- **Table**: State, Year, Total Bills, Enactment Rate
- **Bar Chart**: Top 10 states by total_bills

#### Trends (using `looker_time_series`):
- **Line Chart**: Bills over time by month
- **Stacked Bar**: Positive vs Restrictive by quarter

### 3. Key Filters to Add
- Date Range Control (data_year)
- State Dropdown (state or state_name)
- Intent Filter (positive/neutral/restrictive)
- Policy Area checkboxes

### 4. Google Sheets Integration

For detailed analysis, connect Sheets to BigQuery:

```sql
-- Example query for Sheets
SELECT 
  state_name,
  bill_number,
  description,
  status_category,
  intent,
  enacted_date
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_comprehensive_bills`
WHERE data_year = 2024
  AND state_code = 'CA'
ORDER BY introduced_date DESC
LIMIT 1000;
```

## Performance Tips
- Use `looker_comprehensive_bills` for detailed analysis
- Use aggregated views (`looker_state_summary`) for faster dashboards
- Enable data extract for better performance
- Set reasonable default date ranges

## Next Steps
1. Start with one dashboard using `looker_comprehensive_bills`
2. Test performance and adjust
3. Add more specialized dashboards using other views
4. Share with stakeholders for feedback