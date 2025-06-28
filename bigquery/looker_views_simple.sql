-- Simplified Looker Studio Views for Guttmacher Legislative Tracker
-- Based on actual schema from all_historical_bills_unified

-- 1. Main Bills Dashboard View
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard` AS
SELECT 
  -- Core identifiers
  id,
  data_year,
  state,
  bill_type,
  bill_number,
  CONCAT(state, '-', bill_number, '-', CAST(data_year AS STRING)) as unique_bill_key,
  
  -- Descriptive fields
  description,
  history,
  notes,
  website_blurb,
  internal_summary,
  
  -- Key dates
  last_action_date,
  introduced_date,
  enacted_date,
  vetoed_date,
  date_last_updated,
  effective_date,
  
  -- Status (using available boolean flags)
  CASE 
    WHEN enacted = TRUE THEN 'Enacted'
    WHEN vetoed = TRUE THEN 'Vetoed'
    WHEN dead = TRUE THEN 'Dead'
    WHEN pending = TRUE THEN 'Pending'
    WHEN passed_second_chamber = TRUE THEN 'Passed Both Chambers'
    WHEN passed_first_chamber = TRUE THEN 'Passed One Chamber'
    WHEN seriously_considered = TRUE THEN 'Seriously Considered'
    WHEN introduced = TRUE THEN 'Introduced'
    ELSE 'Unknown'
  END AS status,
  
  -- Intent
  CASE
    WHEN positive = TRUE THEN 'Positive'
    WHEN neutral = TRUE THEN 'Neutral' 
    WHEN restrictive = TRUE THEN 'Restrictive'
    ELSE 'Unclassified'
  END AS intent,
  
  -- Policy areas
  abortion,
  contraception,
  emergency_contraception,
  minors,
  pregnancy,
  refusal,
  sex_education,
  insurance,
  appropriations,
  fetal_issues,
  fetal_tissue,
  incarceration,
  period_products,
  stis,
  
  -- Bill types
  legislation,
  resolution,
  ballot_initiative,
  constitutional_amendment,
  court_case,
  
  -- Topics
  topic_1,
  topic_2,
  topic_3,
  topic_4,
  topic_5,
  topic_6,
  topic_7,
  topic_8,
  topic_9,
  topic_10,
  
  -- Status flags
  introduced,
  seriously_considered,
  passed_first_chamber,
  passed_second_chamber,
  enacted,
  vetoed,
  dead,
  pending,
  positive,
  neutral,
  restrictive,
  
  -- Calculated fields
  DATE_DIFF(enacted_date, introduced_date, DAY) as days_to_enactment,
  DATE_DIFF(last_action_date, introduced_date, DAY) as days_active,
  
  -- Metadata
  migration_date,
  data_source

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE state IS NOT NULL
  AND bill_number IS NOT NULL;

-- 2. State Summary View
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_state_summary` AS
SELECT 
  state,
  data_year,
  COUNT(*) as total_bills,
  COUNT(CASE WHEN enacted = TRUE THEN 1 END) as enacted_bills,
  COUNT(CASE WHEN vetoed = TRUE THEN 1 END) as vetoed_bills,
  COUNT(CASE WHEN positive = TRUE THEN 1 END) as positive_bills,
  COUNT(CASE WHEN neutral = TRUE THEN 1 END) as neutral_bills,
  COUNT(CASE WHEN restrictive = TRUE THEN 1 END) as restrictive_bills,
  
  -- Policy area counts
  COUNT(CASE WHEN abortion = TRUE THEN 1 END) as abortion_bills,
  COUNT(CASE WHEN contraception = TRUE THEN 1 END) as contraception_bills,
  COUNT(CASE WHEN minors = TRUE THEN 1 END) as minors_bills,
  
  -- Rates
  ROUND(COUNT(CASE WHEN enacted = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as enactment_rate

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY state, data_year;

-- 3. Time Series View
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_time_series` AS
SELECT 
  data_year,
  EXTRACT(MONTH FROM introduced_date) as month,
  EXTRACT(QUARTER FROM introduced_date) as quarter,
  state,
  COUNT(*) as bills_introduced,
  COUNT(CASE WHEN enacted = TRUE THEN 1 END) as bills_enacted,
  COUNT(CASE WHEN positive = TRUE THEN 1 END) as positive_bills,
  COUNT(CASE WHEN restrictive = TRUE THEN 1 END) as restrictive_bills

FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE introduced_date IS NOT NULL
GROUP BY data_year, month, quarter, state;

-- 4. Topic Analysis View
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_topic_analysis` AS
WITH topic_unnested AS (
  SELECT 
    data_year,
    state,
    enacted,
    topic
  FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`,
  UNNEST([topic_1, topic_2, topic_3, topic_4, topic_5, topic_6, topic_7, topic_8, topic_9, topic_10]) as topic
  WHERE topic IS NOT NULL
)
SELECT 
  topic,
  data_year,
  COUNT(*) as bill_count,
  COUNT(CASE WHEN enacted = TRUE THEN 1 END) as enacted_count,
  COUNT(DISTINCT state) as states_with_topic
FROM topic_unnested
GROUP BY topic, data_year
ORDER BY data_year DESC, bill_count DESC;