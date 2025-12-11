-- Data Quality Report
-- Replacement for missing tracking_completeness_matrix view
-- Use this query for methodology analysis and data quality checks
--
-- This query uses the existing raw_data_tracking_by_year view
-- to show field tracking completeness across years
--
-- For Looker Studio: Use raw_data_tracking_by_year directly as data source

-- Quick Overview: What fields were tracked each year?
SELECT
  data_year,
  total_bills,

  -- Core field tracking (should always be 100%)
  ROUND(bill_type_tracking_pct, 1) as bill_type_pct,
  ROUND(bill_number_tracking_pct, 1) as bill_number_pct,
  ROUND(state_tracking_pct, 1) as state_pct,

  -- Date tracking evolution
  ROUND(introduced_date_tracking_pct, 1) as introduced_date_pct,
  ROUND(last_action_date_tracking_pct, 1) as last_action_pct,
  ROUND(enacted_date_tracking_pct, 1) as enacted_date_pct,

  -- Status field tracking
  ROUND(introduced_tracking_pct, 1) as introduced_status_pct,
  ROUND(enacted_tracking_pct, 1) as enacted_status_pct,
  ROUND(dead_tracking_pct, 1) as dead_status_pct,

  -- Intent tracking (started 2006+)
  ROUND(positive_tracking_pct, 1) as positive_intent_pct,
  ROUND(restrictive_tracking_pct, 1) as restrictive_intent_pct,

  -- Policy area tracking evolution
  ROUND(abortion_tracking_pct, 1) as abortion_pct,
  ROUND(contraception_tracking_pct, 1) as contraception_pct,
  ROUND(minors_tracking_pct, 1) as minors_pct,
  ROUND(sex_education_tracking_pct, 1) as sex_ed_pct,

  -- Newer fields (started later)
  ROUND(emergency_contraception_tracking_pct, 1) as emergency_contra_pct,
  ROUND(incarceration_tracking_pct, 1) as incarceration_pct,
  ROUND(period_products_tracking_pct, 1) as period_products_pct,

  -- Visual indicators for quick scanning
  CASE
    WHEN abortion_tracking_pct >= 95 THEN '✅ Complete'
    WHEN abortion_tracking_pct >= 50 THEN '⚠️ Partial'
    WHEN abortion_tracking_pct >= 1 THEN '🔶 Minimal'
    ELSE '❌ Not tracked'
  END as abortion_status,

  CASE
    WHEN contraception_tracking_pct >= 95 THEN '✅ Complete'
    WHEN contraception_tracking_pct >= 50 THEN '⚠️ Partial'
    WHEN contraception_tracking_pct >= 1 THEN '🔶 Minimal'
    ELSE '❌ Not tracked'
  END as contraception_status,

  CASE
    WHEN incarceration_tracking_pct >= 95 THEN '✅ Complete'
    WHEN incarceration_tracking_pct >= 50 THEN '⚠️ Partial'
    WHEN incarceration_tracking_pct >= 1 THEN '🔶 Minimal'
    ELSE '❌ Not tracked'
  END as incarceration_status,

  CASE
    WHEN period_products_tracking_pct >= 95 THEN '✅ Complete'
    WHEN period_products_tracking_pct >= 50 THEN '⚠️ Partial'
    WHEN period_products_tracking_pct >= 1 THEN '🔶 Minimal'
    ELSE '❌ Not tracked'
  END as period_products_status

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.raw_data_tracking_by_year`
ORDER BY data_year DESC;

-- Example Usage:
-- 1. Run this query in BigQuery Console for ad-hoc analysis
-- 2. Filter to specific years: WHERE data_year IN (2002, 2010, 2020, 2024)
-- 3. Export to CSV for reports
-- 4. Use raw_data_tracking_by_year directly in Looker Studio for live dashboards
