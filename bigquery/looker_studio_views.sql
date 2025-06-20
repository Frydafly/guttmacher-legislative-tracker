-- BigQuery Views for Looker Studio Analysis - Enhanced Migration Pipeline
-- =============================================================================
-- These views work with the ENHANCED migration pipeline using field mappings
-- Based on standardized schema from field_mappings.yaml
-- Uses all_historical_bills_unified view created by enhanced_migration_pipeline.py

-- =============================================================================
-- 1. MAIN BILLS ANALYSIS VIEW - Primary data source for Looker Studio
-- =============================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_bills_dashboard` AS
SELECT 
  -- Core identifiers
  id,
  data_year,
  state,
  bill_type,
  bill_number,
  CONCAT(state, '-', bill_number, '-', data_year) as unique_bill_key,
  
  -- State name mapping
  CASE state
    WHEN 'AL' THEN 'Alabama' WHEN 'AK' THEN 'Alaska' WHEN 'AZ' THEN 'Arizona'
    WHEN 'AR' THEN 'Arkansas' WHEN 'CA' THEN 'California' WHEN 'CO' THEN 'Colorado'
    WHEN 'CT' THEN 'Connecticut' WHEN 'DE' THEN 'Delaware' WHEN 'FL' THEN 'Florida'
    WHEN 'GA' THEN 'Georgia' WHEN 'HI' THEN 'Hawaii' WHEN 'ID' THEN 'Idaho'
    WHEN 'IL' THEN 'Illinois' WHEN 'IN' THEN 'Indiana' WHEN 'IA' THEN 'Iowa'
    WHEN 'KS' THEN 'Kansas' WHEN 'KY' THEN 'Kentucky' WHEN 'LA' THEN 'Louisiana'
    WHEN 'ME' THEN 'Maine' WHEN 'MD' THEN 'Maryland' WHEN 'MA' THEN 'Massachusetts'
    WHEN 'MI' THEN 'Michigan' WHEN 'MN' THEN 'Minnesota' WHEN 'MS' THEN 'Mississippi'
    WHEN 'MO' THEN 'Missouri' WHEN 'MT' THEN 'Montana' WHEN 'NE' THEN 'Nebraska'
    WHEN 'NV' THEN 'Nevada' WHEN 'NH' THEN 'New Hampshire' WHEN 'NJ' THEN 'New Jersey'
    WHEN 'NM' THEN 'New Mexico' WHEN 'NY' THEN 'New York' WHEN 'NC' THEN 'North Carolina'
    WHEN 'ND' THEN 'North Dakota' WHEN 'OH' THEN 'Ohio' WHEN 'OK' THEN 'Oklahoma'
    WHEN 'OR' THEN 'Oregon' WHEN 'PA' THEN 'Pennsylvania' WHEN 'RI' THEN 'Rhode Island'
    WHEN 'SC' THEN 'South Carolina' WHEN 'SD' THEN 'South Dakota' WHEN 'TN' THEN 'Tennessee'
    WHEN 'TX' THEN 'Texas' WHEN 'UT' THEN 'Utah' WHEN 'VT' THEN 'Vermont'
    WHEN 'VA' THEN 'Virginia' WHEN 'WA' THEN 'Washington' WHEN 'WV' THEN 'West Virginia'
    WHEN 'WI' THEN 'Wisconsin' WHEN 'WY' THEN 'Wyoming'
    ELSE state
  END as state_name,
  
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
  
  -- Status progression (calculated)
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
  END AS status_category,
  
  -- Intent classification
  CASE
    WHEN positive = TRUE THEN 'Positive'
    WHEN neutral = TRUE THEN 'Neutral' 
    WHEN restrictive = TRUE THEN 'Restrictive'
    ELSE 'Unclassified'
  END AS intent,
  
  -- Policy areas (major categories)
  abortion,
  contraception,
  emergency_contraception,
  minors,
  pregnancy,
  refusal,
  sex_education,
  insurance,
  appropriations,
  
  -- Newer policy areas
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
  
  -- Topics/Subpolicies (consolidated)
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
  
  -- Calculated fields for analysis
  DATE_DIFF(enacted_date, introduced_date, DAY) as days_to_enactment,
  DATE_DIFF(last_action_date, introduced_date, DAY) as days_since_introduction,
  
  -- Policy area count (how many policy areas this bill touches)
  (CAST(abortion AS INT64) +
   CAST(contraception AS INT64) +
   CAST(emergency_contraception AS INT64) +
   CAST(minors AS INT64) +
   CAST(pregnancy AS INT64) +
   CAST(refusal AS INT64) +
   CAST(sex_education AS INT64) +
   CAST(insurance AS INT64) +
   CAST(appropriations AS INT64) +
   CAST(fetal_issues AS INT64) +
   CAST(fetal_tissue AS INT64) +
   CAST(incarceration AS INT64) +
   CAST(period_products AS INT64) +
   CAST(stis AS INT64)) as policy_area_count,
  
  -- Time periods for trend analysis
  CASE 
    WHEN data_year BETWEEN 2005 AND 2009 THEN '2005-2009'
    WHEN data_year BETWEEN 2010 AND 2014 THEN '2010-2014'
    WHEN data_year BETWEEN 2015 AND 2019 THEN '2015-2019'
    WHEN data_year BETWEEN 2020 AND 2024 THEN '2020-2024'
    ELSE 'Other'
  END as time_period,
  
  -- Metadata
  migration_date,
  data_source

FROM `{project_id}.{dataset_id}.all_historical_bills_unified`
WHERE state IS NOT NULL
  AND bill_number IS NOT NULL;

-- =====================================================================
-- Summary Statistics for High-Level KPIs
-- =====================================================================
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_summary` AS
SELECT 
    -- Aggregation dimensions
    data_year,
    state_code,
    state_name,
    status_category,
    
    -- Core metrics
    COUNT(*) as total_bills,
    COUNT(CASE WHEN is_enacted THEN 1 END) as enacted_bills,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as vetoed_bills,
    COUNT(CASE WHEN passed_both_houses THEN 1 END) as bills_passed_both_houses,
    
    -- Policy area counts
    COUNT(CASE WHEN is_abortion_related THEN 1 END) as abortion_bills,
    COUNT(CASE WHEN is_family_planning THEN 1 END) as family_planning_bills,
    COUNT(CASE WHEN is_teen_issues THEN 1 END) as teen_issue_bills,
    COUNT(CASE WHEN is_fetal_rights THEN 1 END) as fetal_rights_bills,
    COUNT(CASE WHEN is_insurance_related THEN 1 END) as insurance_bills,
    
    -- Calculated percentages
    ROUND(COUNT(CASE WHEN is_enacted THEN 1 END) * 100.0 / COUNT(*), 1) as enactment_rate,
    ROUND(COUNT(CASE WHEN is_vetoed THEN 1 END) * 100.0 / COUNT(*), 1) as veto_rate,
    ROUND(COUNT(CASE WHEN is_abortion_related THEN 1 END) * 100.0 / COUNT(*), 1) as abortion_rate,
    ROUND(COUNT(CASE WHEN is_family_planning THEN 1 END) * 100.0 / COUNT(*), 1) as family_planning_rate,
    
    -- Data freshness
    MAX(last_updated) as data_last_updated,
    COUNT(DISTINCT primary_issue) as unique_issues_count
    
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard`
GROUP BY data_year, state_code, state_name, status_category;

-- =====================================================================
-- Policy Categories View for Issue Analysis
-- =====================================================================
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_policy_categories` AS
SELECT 
    data_year,
    CAST(data_year AS INT64) as data_year_int,
    specific_monitoring_category as category_name,
    COUNT(*) as category_count,
    data_source,
    MAX(SAFE.PARSE_DATE('%Y-%m-%d', migration_date)) as migration_date
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_categories`
WHERE specific_monitoring_category IS NOT NULL
GROUP BY data_year, specific_monitoring_category, data_source;

-- =====================================================================
-- Time Series Analysis View
-- =====================================================================
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_time_series` AS
SELECT 
    -- Time dimensions
    data_year,
    action_year,
    action_month,
    CASE action_month
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        WHEN 12 THEN 'December'
    END as action_month_name,
    action_quarter,
    
    -- Geographic dimension
    state_code,
    state_name,
    
    -- Metrics by time period
    COUNT(*) as bills_total,
    COUNT(CASE WHEN is_enacted THEN 1 END) as bills_enacted,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as bills_vetoed,
    COUNT(CASE WHEN is_abortion_related THEN 1 END) as abortion_bills,
    COUNT(CASE WHEN is_family_planning THEN 1 END) as family_planning_bills,
    
    -- Activity indicators
    CASE 
        WHEN COUNT(*) >= 20 THEN 'High Activity'
        WHEN COUNT(*) >= 10 THEN 'Medium Activity'
        WHEN COUNT(*) >= 5 THEN 'Low Activity'
        ELSE 'Very Low Activity'
    END as activity_level
    
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard`
WHERE action_year IS NOT NULL AND action_month IS NOT NULL
GROUP BY 
    data_year, action_year, action_month, action_quarter,
    state_code, state_name
ORDER BY action_year DESC, action_month DESC, state_code;

-- =====================================================================
-- Geographic Analysis View
-- =====================================================================
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_geographic_analysis` AS
SELECT 
    state_code,
    state_name,
    
    -- Overall statistics
    COUNT(*) as total_bills_all_years,
    COUNT(DISTINCT data_year) as years_with_data,
    MIN(data_year) as first_year,
    MAX(data_year) as last_year,
    
    -- By policy area
    COUNT(CASE WHEN is_abortion_related THEN 1 END) as total_abortion_bills,
    COUNT(CASE WHEN is_family_planning THEN 1 END) as total_family_planning_bills,
    COUNT(CASE WHEN is_teen_issues THEN 1 END) as total_teen_bills,
    COUNT(CASE WHEN is_fetal_rights THEN 1 END) as total_fetal_rights_bills,
    
    -- By outcome
    COUNT(CASE WHEN is_enacted THEN 1 END) as total_enacted,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as total_vetoed,
    
    -- Rates
    ROUND(COUNT(CASE WHEN is_abortion_related THEN 1 END) * 100.0 / COUNT(*), 1) as abortion_rate,
    ROUND(COUNT(CASE WHEN is_family_planning THEN 1 END) * 100.0 / COUNT(*), 1) as family_planning_rate,
    ROUND(COUNT(CASE WHEN is_enacted THEN 1 END) * 100.0 / COUNT(*), 1) as enactment_rate,
    
    -- Activity level categorization
    CASE 
        WHEN COUNT(*) >= 50 THEN 'High Activity'
        WHEN COUNT(*) >= 25 THEN 'Medium Activity'
        WHEN COUNT(*) >= 10 THEN 'Low Activity'
        ELSE 'Very Low Activity'
    END as activity_level,
    
    -- Top issues
    (SELECT primary_issue 
     FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard` b2
     WHERE b2.state_code = b1.state_code AND b2.primary_issue IS NOT NULL
     GROUP BY primary_issue 
     ORDER BY COUNT(*) DESC 
     LIMIT 1) as top_issue
    
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard` b1
GROUP BY state_code, state_name
ORDER BY total_bills_all_years DESC;

-- =====================================================================
-- Issue Analysis View
-- =====================================================================
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.looker_issue_analysis` AS
SELECT 
    primary_issue,
    data_year,
    
    -- Counts
    COUNT(*) as bills_count,
    COUNT(CASE WHEN is_enacted THEN 1 END) as enacted_count,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as vetoed_count,
    COUNT(DISTINCT state_code) as states_with_bills,
    
    -- Rates
    ROUND(COUNT(CASE WHEN is_enacted THEN 1 END) * 100.0 / COUNT(*), 1) as enactment_rate,
    ROUND(COUNT(CASE WHEN is_vetoed THEN 1 END) * 100.0 / COUNT(*), 1) as veto_rate,
    
    -- Top states for this issue
    (SELECT state_code 
     FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard` b2
     WHERE b2.primary_issue = b1.primary_issue AND b2.data_year = b1.data_year
     GROUP BY state_code 
     ORDER BY COUNT(*) DESC 
     LIMIT 1) as top_state,
     
    -- Activity level
    CASE 
        WHEN COUNT(*) >= 20 THEN 'High Volume Issue'
        WHEN COUNT(*) >= 10 THEN 'Medium Volume Issue'
        WHEN COUNT(*) >= 5 THEN 'Low Volume Issue'
        ELSE 'Rare Issue'
    END as issue_volume
    
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_bills_dashboard` b1
WHERE primary_issue IS NOT NULL
GROUP BY primary_issue, data_year
ORDER BY data_year DESC, bills_count DESC;