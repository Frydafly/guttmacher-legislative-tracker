# Looker Studio Guide

## Overview

Looker Studio (formerly Google Data Studio) is a free data visualization tool that connects to our BigQuery historical legislative data. This guide helps you improve and use interactive dashboards to explore 22 years of legislative tracking data (2002-2024).

!!! tip "Who This Guide Is For"
    - Policy team members who need to visualize data trends
    - Analysts creating reports for stakeholders
    - Anyone who wants to explore legislative data without writing SQL

## Accessing Looker Studio

1. Go to [lookerstudio.google.com](https://lookerstudio.google.com)
2. Sign in with your Google Account
3. Open existing dashboards or create new ones

!!! info "Need Access?"
    If you can't access the Guttmacher Legislative Tracker dashboard, contact your administrator to grant you Viewer or Editor permissions.

---

## Improving Your Dashboard

### Current State Analysis

If you have an existing dashboard, evaluate it against these criteria:

**What's Working:**
✅ Connected to BigQuery data
✅ Shows basic charts and tables
✅ Updates when data changes

**What Needs Improvement:**
❌ Hard to filter data by state, year, or policy area
❌ Too much clutter - unclear where to look
❌ No way to drill down into details
❌ Can't export filtered results easily

---

## Recommended Improvements

### 1. Add Interactive Filters (Priority: HIGH)

Interactive filters let users explore data without technical knowledge.

#### Essential Filters to Add:

=== "Date Range Filter"

    **Where:** Top of dashboard (most prominent position)

    **How to add:**

    1. Click "Add a control" → "Date range control"
    2. Connect to dimension: `data_year` or `introduced_date`
    3. Set default: "Current year" or "Last 12 months"
    4. Position: Top-left corner

    **Why:** Users need to quickly switch between current session and historical data

=== "State Dropdown"

    **Where:** Top of dashboard, next to date range

    **How to add:**

    1. Click "Add a control" → "Drop-down list"
    2. Connect to dimension: `state` or `state_name`
    3. Enable "Select all" option
    4. Sort alphabetically

    **Why:** Most common question is "Show me [state] bills"

=== "Policy Area Checkboxes"

    **Where:** Top section, below date and state

    **How to add:**

    1. Click "Add a control" → "Checkbox list"
    2. Create calculated field combining all policy booleans
    3. Or add separate checkboxes for each: abortion, contraception, minors, etc.

    **Why:** Users want to filter by specific policy topics

=== "Intent Filter"

    **Where:** Next to policy area filters

    **How to add:**

    1. Click "Add a control" → "Drop-down list"
    2. Connect to dimension: `intent` (Protective/Restrictive/Neutral)
    3. Enable multi-select

    **Why:** Critical for analyzing protective vs. restrictive legislation

!!! example "Filter Layout Example"
    ```
    ┌──────────────────────────────────────────────────────┐
    │  📅 Date: [2024 ▼]  📍 State: [All states ▼]       │
    │  📋 Policy: ☑ Abortion ☑ Contraception ☐ Minors    │
    │  🎯 Intent: ☑ Protective ☑ Restrictive ☐ Neutral  │
    └──────────────────────────────────────────────────────┘
    ```

---

### 2. Reorganize Dashboard Layout (Priority: HIGH)

Use the "F-pattern" reading flow - users scan top-to-bottom, left-to-right.

#### Recommended Layout:

```
┌─────────────────────────────────────────────────┐
│  FILTERS (Date, State, Policy, Intent)          │ ← Most important
├─────────────────────────────────────────────────┤
│  📊 KEY METRICS (Scorecards)                    │
│  ┌─────────┬─────────┬─────────┬─────────┐     │
│  │ Total   │ Enacted │ % Rest. │ States  │     │
│  │ Bills   │ Bills   │ Bills   │ Active  │     │
│  └─────────┴─────────┴─────────┴─────────┘     │
├─────────────────────────────────────────────────┤
│  📈 TRENDS & COMPARISONS                        │
│  ┌──────────────────┬──────────────────┐        │
│  │  Line Chart:     │  Bar Chart:      │        │
│  │  Bills over      │  Bills by        │        │
│  │  Time            │  State           │        │
│  └──────────────────┴──────────────────┘        │
├─────────────────────────────────────────────────┤
│  📋 DETAILED DATA TABLE                         │
│  (Filtered bills with all fields)               │
│  [Download this data ↓]                         │
└─────────────────────────────────────────────────┘
```

#### Implementation Steps:

1. **Clear the clutter:** Delete any unused charts or duplicates
2. **Group by purpose:** Filters → Metrics → Trends → Details
3. **Use consistent spacing:** 20px padding between sections
4. **Add section headers:** Clear text labels like "📊 Key Metrics"

---

### 3. Add Drill-Down Features (Priority: MEDIUM)

Let users click on charts to see more details.

#### How to Enable Drill-Down:

**On Geographic Maps:**

1. Select the map chart
2. Chart settings → "Interactions" → Enable "Enable drill-down"
3. Set dimension hierarchy: `state` → `bill_number`
4. Now users can click a state to see individual bills

**On Bar Charts:**

1. Select bar chart (e.g., "Bills by State")
2. Enable "Cross-filtering"
3. When user clicks a state bar, entire dashboard filters to that state

**On Time Series:**

1. Create dimension hierarchy: `data_year` → `quarter` → `month`
2. Enable drill-down on line chart
3. Users can click year to see quarterly/monthly breakdowns

!!! tip "Make Drill-Down Obvious"
    Add text near interactive charts: "💡 Click any state to see bills" or "Click bars to filter dashboard"

---

### 4. Add Export Capabilities (Priority: HIGH)

Users often need to download filtered data for reports.

#### Method 1: Built-in Export

Every chart has a download option:

1. Hover over any chart
2. Click ⋮ (three dots menu)
3. Select "Download" → CSV or Google Sheets

**Add instructions on dashboard:**
"To export filtered data: Click ⋮ on any chart → Download"

#### Method 2: Export Button

Create a dedicated export button:

1. Add text box with hyperlink
2. Link to BigQuery SQL query that matches dashboard filters
3. Or link to Google Sheets Connected Sheet template

---

### 5. Use 2025 Best Practices

#### The 3-Second Rule

> Each chart should tell a clear story within 3 seconds

**Do:**
✅ Clear chart titles: "Abortion Bills Increased 45% Since 2020"
✅ Prominent data labels showing key numbers
✅ Simple color coding (Protective=Green, Restrictive=Red, Neutral=Gray)

**Don't:**
❌ Vague titles: "Chart 1" or "Data Visualization"
❌ Too many colors/categories
❌ Tiny fonts or cluttered legends

#### Avoid Jargon

Replace technical terms with plain language:

| ❌ Technical | ✅ Plain Language |
|-------------|-------------------|
| "CTR" | "Click Rate" or explain what it means |
| "Enacted flag=TRUE" | "Passed into law" |
| "data_year" | "Legislative Session Year" |
| "Seriously Considered" | "Advanced in Committee" |

#### Use Conditional Formatting

Highlight important trends automatically:

- **Red:** When restrictive bills > 60% (concerning)
- **Yellow:** When enactment rate < 5% (unusual)
- **Green:** When protective bills increasing year-over-year

---

## Using the Dashboard (For End Users)

### Common Questions & How to Answer Them

=== "How many bills in [State] last year?"

    **Steps:**

    1. Set Date Range to previous year (e.g., 2024)
    2. Select State from dropdown
    3. Look at "Total Bills" scorecard

    **Faster:** Use AI/Gemini if available (see below)

=== "Which states have the most restrictive bills?"

    **Steps:**

    1. Set Intent filter to "Restrictive"
    2. Look at "Bills by State" bar chart
    3. States are sorted by count

    **Export:** Click ⋮ on chart → Download to see full list

=== "Are abortion bills increasing?"

    **Steps:**

    1. Set Policy filter to "Abortion"
    2. Look at "Bills Over Time" line chart
    3. Check trend direction

    **Drill down:** Click chart to see yearly, quarterly, or monthly detail

=== "Show me all enacted protective bills from 2023"

    **Steps:**

    1. Date Range: 2023
    2. Intent: Protective
    3. Status: Enacted (if you have this filter)
    4. Scroll to bottom "Detailed Data Table"
    5. Export table as CSV

---

### Using AI-Powered Features (NEW in 2025)

If your Looker Studio has Gemini AI integration:

!!! success "Ask Questions in Plain English"
    Instead of clicking filters, just type:

    - "How many California abortion bills passed in 2024?"
    - "Show me restrictive bills by state"
    - "What's the trend in contraception legislation?"

    Gemini generates charts and answers automatically!

**How to enable:**

1. Check if "Ask a question" search bar appears at top of dashboard
2. If not, check Google Workspace admin settings
3. Or contact IT to enable Gemini for Looker Studio

---

## Connecting Your Dashboard to BigQuery

### Available Data Sources

Connect to these BigQuery views:

=== "looker_bills_dashboard"

    **Best for:** General-purpose dashboards

    **Contains:**

    - All bill details (description, dates, status)
    - Policy areas (abortion, contraception, etc.)
    - Intent (protective/restrictive/neutral)
    - Topics and subcategories

    **Use when:** Building comprehensive dashboards

=== "looker_state_summary"

    **Best for:** State-level comparisons

    **Contains:**

    - Pre-aggregated state metrics
    - Bills by state and year
    - Enactment rates
    - Policy area counts

    **Use when:** Dashboard performance is slow with full dataset

=== "looker_time_series"

    **Best for:** Trend analysis

    **Contains:**

    - Monthly/quarterly breakdowns
    - Bills introduced and enacted over time
    - Intent trends

    **Use when:** Creating line charts and time-based analysis

=== "comprehensive_bills_authentic"

    **Best for:** Most detailed analysis

    **Contains:**

    - All fields from `looker_bills_dashboard`
    - Plus calculated fields (days_to_enactment, etc.)
    - Regional groupings
    - Enhanced categorizations

    **Use when:** Need every possible data point

### How to Connect:

1. In Looker Studio, click "Add data" → "BigQuery"
2. Select: `guttmacher-legislative-tracker` project
3. Select: `legislative_tracker_historical` dataset
4. Choose view (e.g., `looker_bills_dashboard`)
5. Click "Add"

!!! warning "Need Permissions?"
    If you can't see the BigQuery project, you need BigQuery Data Viewer access.
    See: [External User Access Guide](../technical/external-user-access.md)

---

## Dashboard Checklist

Use this checklist when building or reviewing dashboards:

### Setup
- [ ] Connected to correct BigQuery view
- [ ] Data refresh schedule set (daily or real-time)
- [ ] Correct date field selected as default dimension

### Filters & Controls
- [ ] Date range filter (top-left, prominent)
- [ ] State dropdown (with "All states" default)
- [ ] Policy area checkboxes or dropdown
- [ ] Intent filter (Protective/Restrictive/Neutral)
- [ ] All filters apply to entire dashboard

### Visual Organization
- [ ] Filters at top of page
- [ ] Key metrics (scorecards) immediately below filters
- [ ] Charts in logical groupings (trends, comparisons, geographic)
- [ ] Detailed table at bottom
- [ ] Consistent spacing and alignment

### Interactivity
- [ ] Click charts to filter (cross-filtering enabled)
- [ ] Drill-down enabled on geographic maps
- [ ] Hover tooltips show relevant details
- [ ] Instructions visible for non-technical users

### User Experience
- [ ] Chart titles are descriptive, not technical
- [ ] No jargon or undefined acronyms
- [ ] Color coding is consistent (Protective=Green, etc.)
- [ ] Export instructions visible
- [ ] "Help" or "How to Use" text included

### Performance
- [ ] Dashboard loads in < 5 seconds
- [ ] Consider using aggregated views for large datasets
- [ ] Set reasonable default filters (e.g., "Current year" not "All years")

---

## Troubleshooting

### Dashboard is Slow

**Solution 1:** Use pre-aggregated views

- Switch from `looker_bills_dashboard` to `looker_state_summary`
- Reduces data volume while maintaining accuracy

**Solution 2:** Set default filters

- Default date range to "Current year" instead of "All time"
- Reduces initial data load

**Solution 3:** Enable data extract

- Data source settings → "Enable data extract"
- Caches data for faster performance

### Filters Don't Work

**Check:**

1. Filter is connected to correct field name
2. Filter applies to all charts (not just one)
3. Field has data (e.g., some years may not have `enacted_date`)

**Fix:**

- Select filter → "Filter control settings" → "Apply to all charts"

### Can't See BigQuery Data

**Error:** "You don't have access to this data source"

**Solution:**

1. Verify you have BigQuery access (see [External User Access](../technical/external-user-access.md))
2. Check if you're using correct Google Account
3. Ask dashboard owner to share with you as "Viewer" or "Editor"

### Charts Show Wrong Data

**Check:**

1. Date range filter - is it set to expected time period?
2. Field aggregation - should be COUNT, SUM, or AVG?
3. Filters applied - hidden filters might be limiting data

**Fix:**

- Clear all filters and rebuild one at a time
- Check data source preview to verify data exists

---

## Advanced Features

### Parameters (Dynamic Values)

Create parameters for "what-if" scenarios:

**Example:** "Show me if restrictive bills increased by X%"

1. Create parameter: `increase_percentage`
2. Create calculated field: `restrictive_bills * (1 + increase_percentage)`
3. Add slider control for users to adjust percentage

### Calculated Fields

Useful calculated fields for legislative data:

```sql
-- Enactment Rate
COUNT(CASE WHEN enacted = TRUE THEN 1 END) / COUNT(*) * 100

-- Days to Passage
DATE_DIFF(enacted_date, introduced_date, DAY)

-- Policy Complexity (how many policy areas)
(CASE WHEN abortion THEN 1 ELSE 0 END) +
(CASE WHEN contraception THEN 1 ELSE 0 END) +
(CASE WHEN minors THEN 1 ELSE 0 END)
-- ... etc

-- Regional Grouping
CASE
  WHEN state IN ('CA', 'OR', 'WA') THEN 'West Coast'
  WHEN state IN ('TX', 'AZ', 'NM') THEN 'Southwest'
  -- ... etc
END
```

### Embedding Dashboards

Share dashboards with external partners:

1. Click "Share" → "Get report link"
2. Set permissions: "Anyone with link can view"
3. Or embed in website: "File" → "Embed report"

!!! warning "Security Note"
    Only share dashboards publicly if data is meant for external consumption.
    For internal use, keep "Restricted" sharing and add users individually.

---

## Next Steps

**After improving your dashboard:**

1. **Test with real users:** Ask policy team to try using it
2. **Gather feedback:** What questions can't they answer?
3. **Iterate:** Add filters/charts based on actual needs
4. **Document:** Add "How to Use" section on dashboard itself

**Related Resources:**

- [BigQuery for Analysts](bigquery-for-analysts.md) - Write SQL queries for custom analysis
- [External User Access](../technical/external-user-access.md) - Grant BigQuery access to collaborators
- [Data Dictionary](../reference/data-dictionary.md) - Understand field definitions

---

## Getting Help

- **Dashboard questions:** Contact your Looker Studio administrator
- **Data questions:** See [BigQuery for Analysts](bigquery-for-analysts.md)
- **Access issues:** See [External User Access](../technical/external-user-access.md)
- **Technical issues:** Contact Fryda Guedes (fryda.guedes@proton.me)

---

*Last updated: December 2025*
