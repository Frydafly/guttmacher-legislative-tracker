# BigQuery Analytics Tables Documentation

## Overview

This directory contains SQL definitions for comprehensive analytics tables that provide state-by-state, year-by-year breakdowns of legislative activity. These tables are **materialized** (not views) for optimal Looker Studio performance.

## Key Concept: TRUE/FALSE/NULL Handling

**IMPORTANT**: These analytics properly distinguish between:
- **TRUE**: Bill explicitly relates to this category
- **FALSE**: Bill explicitly does NOT relate to this category  
- **NULL**: Category was not tracked in that year (data not available)

For example:
- `period_products = FALSE` in 2020 → Bill was evaluated but doesn't relate to period products
- `period_products = NULL` in 2005 → Period products category didn't exist yet in 2005

## Analytics Tables Created

### 1. `state_year_policy_analytics`
**Purpose**: Policy category breakdowns by state and year
**Use Case**: "How many abortion-related bills did Texas have in 2022?"

**Key Columns**:
```sql
-- Raw counts for each policy area
abortion_true, abortion_false, abortion_null
contraception_true, contraception_false, contraception_null
minors_true, minors_false, minors_null
-- ... (all policy categories)

-- Percentages of total bills
abortion_true_pct, contraception_true_pct, etc.

-- Reference data
total_bills, state, data_year
```

**Example Query**:
```sql
SELECT state, data_year, 
       abortion_true, 
       abortion_true_pct,
       total_bills
FROM `project.dataset.state_year_policy_analytics`
WHERE state = 'TX' AND data_year >= 2020
ORDER BY data_year;
```

### 2. `state_year_status_analytics`
**Purpose**: Bill progression/status by state and year
**Use Case**: "What's California's success rate for getting bills enacted?"

**Key Columns**:
```sql
-- Counts
introduced_count, enacted_count, vetoed_count, dead_count

-- Success metrics
success_rate_pct          -- enacted/introduced
completion_rate_pct       -- (enacted+vetoed)/introduced

-- Percentages of all bills
enacted_pct, vetoed_pct, etc.
```

**Example Query**:
```sql
SELECT state, data_year,
       introduced_count,
       enacted_count, 
       success_rate_pct
FROM `project.dataset.state_year_status_analytics`
WHERE state = 'CA'
ORDER BY data_year;
```

### 3. `state_year_intent_analytics`
**Purpose**: Intent classification (Positive/Neutral/Restrictive) by state and year
**Use Case**: "Which states have the most restrictive bills?"

**Key Columns**:
```sql
-- Raw counts
positive_true, neutral_true, restrictive_true
positive_null, neutral_null, restrictive_null

-- Percentages (of all bills)
positive_pct_all, restrictive_pct_all

-- Percentages (of bills where intent was tracked)
positive_pct_tracked, restrictive_pct_tracked

-- Data availability
intent_tracking_coverage_pct  -- % of bills where intent was tracked
```

**Example Query**:
```sql
SELECT state, data_year,
       restrictive_true,
       restrictive_pct_tracked,
       intent_tracking_coverage_pct
FROM `project.dataset.state_year_intent_analytics`
WHERE data_year >= 2015  -- Intent tracking started around 2015
ORDER BY restrictive_pct_tracked DESC;
```

### 4. `state_year_billtype_analytics`
**Purpose**: Bill type classification (Legislation/Resolution/Constitutional Amendment/etc.)
**Use Case**: "How many constitutional amendments related to reproductive health?"

**Key Columns**:
```sql
-- Raw counts
legislation_true, resolution_true, constitutional_amendment_true
ballot_initiative_true

-- Percentages and coverage
legislation_pct_tracked, resolution_pct_tracked
type_tracking_coverage_pct
```

### 5. `comprehensive_time_series`
**Purpose**: All key metrics combined in one table for easy Looker charting
**Use Case**: Main table for Looker Studio dashboards and time series analysis

**Key Columns**: Combines the most important columns from all other analytics tables:
```sql
-- Core data
state, data_year, total_bills

-- Top policy areas (counts + percentages)
abortion_true, contraception_true, minors_true
abortion_true_pct, contraception_true_pct, minors_true_pct

-- Status metrics
introduced_count, enacted_count, success_rate_pct

-- Intent metrics (when available)
positive_true, restrictive_true, intent_tracking_coverage_pct

-- Bill type metrics (when available)  
legislation_true, resolution_true, type_tracking_coverage_pct
```

### 6. `national_time_series`
**Purpose**: National totals aggregated across all states
**Use Case**: "National trends in reproductive health legislation"

**Key Columns**:
```sql
-- National totals
total_bills_national, states_with_data
abortion_bills_national, contraception_bills_national

-- National success rates
national_success_rate_pct

-- Coverage metrics
avg_intent_coverage_pct, avg_type_coverage_pct
```

## Data Evolution Timeline

Understanding when categories were tracked helps interpret NULL values:

### Early Period (2005-2008)
- **Core categories**: abortion, contraception, minors, insurance, appropriations
- **Status tracking**: Basic (introduced, enacted, vetoed, dead)
- **Intent/Type**: Not tracked (expect NULLs)

### Expansion Period (2009-2014)  
- **Added**: emergency_contraception, refusal, fetal_issues
- **Status tracking**: Enhanced (seriously_considered, chamber passage)
- **Intent/Type**: Not tracked (expect NULLs)

### Modern Period (2015+)
- **Added**: All current categories
- **Intent tracking**: Started (positive, neutral, restrictive)
- **Bill type tracking**: Started (legislation, resolution, etc.)

### Recent Period (2019+)
- **Added**: court_case, period_products, incarceration, STIs
- **Full tracking**: All categories and classifications

## Common Looker Studio Queries

### 1. State Comparison Dashboard
```sql
SELECT state, data_year,
       total_bills,
       abortion_true_pct,
       contraception_true_pct,
       success_rate_pct
FROM `project.dataset.comprehensive_time_series`
WHERE data_year >= 2015
```

### 2. National Trends Chart
```sql
SELECT data_year,
       total_bills_national,
       abortion_bills_national,
       national_success_rate_pct
FROM `project.dataset.national_time_series`
ORDER BY data_year
```

### 3. Policy Focus Analysis
```sql
SELECT state, 
       SUM(abortion_true) as total_abortion_bills,
       SUM(contraception_true) as total_contraception_bills,
       AVG(success_rate_pct) as avg_success_rate
FROM `project.dataset.comprehensive_time_series`
WHERE data_year BETWEEN 2018 AND 2023
GROUP BY state
ORDER BY total_abortion_bills DESC
```

### 4. Data Availability Report
```sql
SELECT data_year,
       AVG(intent_tracking_coverage_pct) as avg_intent_coverage,
       AVG(type_tracking_coverage_pct) as avg_type_coverage,
       COUNT(DISTINCT state) as states_with_data
FROM `project.dataset.comprehensive_time_series`
GROUP BY data_year
ORDER BY data_year
```

## Performance Notes

1. **Tables vs Views**: All analytics are materialized tables for fast Looker Studio performance
2. **Clustering**: Main tables are clustered by (state, data_year) for optimal filtering
3. **Update Frequency**: Tables are recreated when new data is added via migration or add_year.py
4. **Data Size**: Analytics tables are much smaller than raw data, optimized for dashboard queries

## Best Practices

1. **Always filter by data_year** when possible to improve performance
2. **Use coverage metrics** to understand data availability before analysis
3. **Check NULL vs FALSE** carefully when interpreting policy categories
4. **Use comprehensive_time_series** as your primary table for most Looker dashboards
5. **Use national_time_series** for high-level trend analysis

## Regenerating Analytics

Analytics tables are automatically created/updated when you run:
```bash
python migrate.py              # Full migration
python add_year.py 2025        # Add new year
```

To manually recreate just the analytics:
```bash
# The analytics views are created by the create_analytics_views() method
# in migrate.py, which processes sql/state_year_analytics.sql
```

## Questions or Issues?

If you need additional analytics or modifications to existing tables, update the SQL in `state_year_analytics.sql` and re-run the migration to recreate the tables.