-- GUTTMACHER LEGISLATIVE TRACKER: STATE/YEAR ANALYTICS VIEWS
-- ============================================================
-- Comprehensive aggregation views for time series and state analysis
-- Provides TRUE/FALSE/NULL counts for each boolean category by state and year

-- 1. POLICY CATEGORY ANALYTICS BY STATE AND YEAR (MATERIALIZED TABLE FOR LOOKER PERFORMANCE)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.state_year_policy_analytics` AS
WITH policy_categories AS (
  SELECT 
    state,
    data_year,
    -- Policy Category Counts
    COUNTIF(abortion IS TRUE) as abortion_true,
    COUNTIF(abortion IS FALSE) as abortion_false, 
    COUNTIF(abortion IS NULL) as abortion_null,
    
    COUNTIF(contraception IS TRUE) as contraception_true,
    COUNTIF(contraception IS FALSE) as contraception_false,
    COUNTIF(contraception IS NULL) as contraception_null,
    
    COUNTIF(emergency_contraception IS TRUE) as emergency_contraception_true,
    COUNTIF(emergency_contraception IS FALSE) as emergency_contraception_false,
    COUNTIF(emergency_contraception IS NULL) as emergency_contraception_null,
    
    COUNTIF(minors IS TRUE) as minors_true,
    COUNTIF(minors IS FALSE) as minors_false,
    COUNTIF(minors IS NULL) as minors_null,
    
    COUNTIF(pregnancy IS TRUE) as pregnancy_true,
    COUNTIF(pregnancy IS FALSE) as pregnancy_false,
    COUNTIF(pregnancy IS NULL) as pregnancy_null,
    
    COUNTIF(refusal IS TRUE) as refusal_true,
    COUNTIF(refusal IS FALSE) as refusal_false,
    COUNTIF(refusal IS NULL) as refusal_null,
    
    COUNTIF(sex_education IS TRUE) as sex_education_true,
    COUNTIF(sex_education IS FALSE) as sex_education_false,
    COUNTIF(sex_education IS NULL) as sex_education_null,
    
    COUNTIF(insurance IS TRUE) as insurance_true,
    COUNTIF(insurance IS FALSE) as insurance_false,
    COUNTIF(insurance IS NULL) as insurance_null,
    
    COUNTIF(appropriations IS TRUE) as appropriations_true,
    COUNTIF(appropriations IS FALSE) as appropriations_false,
    COUNTIF(appropriations IS NULL) as appropriations_null,
    
    COUNTIF(fetal_issues IS TRUE) as fetal_issues_true,
    COUNTIF(fetal_issues IS FALSE) as fetal_issues_false,
    COUNTIF(fetal_issues IS NULL) as fetal_issues_null,
    
    COUNTIF(fetal_tissue IS TRUE) as fetal_tissue_true,
    COUNTIF(fetal_tissue IS FALSE) as fetal_tissue_false,
    COUNTIF(fetal_tissue IS NULL) as fetal_tissue_null,
    
    COUNTIF(incarceration IS TRUE) as incarceration_true,
    COUNTIF(incarceration IS FALSE) as incarceration_false,
    COUNTIF(incarceration IS NULL) as incarceration_null,
    
    COUNTIF(period_products IS TRUE) as period_products_true,
    COUNTIF(period_products IS FALSE) as period_products_false,
    COUNTIF(period_products IS NULL) as period_products_null,
    
    COUNTIF(stis IS TRUE) as stis_true,
    COUNTIF(stis IS FALSE) as stis_false,
    COUNTIF(stis IS NULL) as stis_null,
    
    -- Total bills for reference
    COUNT(*) as total_bills
    
  FROM `{{ project_id }}.{{ dataset_id }}.all_historical_bills_materialized`
  GROUP BY state, data_year
)
SELECT 
  state,
  data_year,
  total_bills,
  
  -- Abortion
  abortion_true,
  abortion_false,
  abortion_null,
  SAFE_DIVIDE(abortion_true, total_bills) * 100 as abortion_true_pct,
  
  -- Contraception
  contraception_true,
  contraception_false, 
  contraception_null,
  SAFE_DIVIDE(contraception_true, total_bills) * 100 as contraception_true_pct,
  
  -- Emergency Contraception
  emergency_contraception_true,
  emergency_contraception_false,
  emergency_contraception_null,
  SAFE_DIVIDE(emergency_contraception_true, total_bills) * 100 as emergency_contraception_true_pct,
  
  -- Minors
  minors_true,
  minors_false,
  minors_null,
  SAFE_DIVIDE(minors_true, total_bills) * 100 as minors_true_pct,
  
  -- Pregnancy
  pregnancy_true,
  pregnancy_false,
  pregnancy_null,
  SAFE_DIVIDE(pregnancy_true, total_bills) * 100 as pregnancy_true_pct,
  
  -- Refusal
  refusal_true,
  refusal_false,
  refusal_null,
  SAFE_DIVIDE(refusal_true, total_bills) * 100 as refusal_true_pct,
  
  -- Sex Education
  sex_education_true,
  sex_education_false,
  sex_education_null,
  SAFE_DIVIDE(sex_education_true, total_bills) * 100 as sex_education_true_pct,
  
  -- Insurance
  insurance_true,
  insurance_false,
  insurance_null,
  SAFE_DIVIDE(insurance_true, total_bills) * 100 as insurance_true_pct,
  
  -- Appropriations
  appropriations_true,
  appropriations_false,
  appropriations_null,
  SAFE_DIVIDE(appropriations_true, total_bills) * 100 as appropriations_true_pct,
  
  -- Fetal Issues
  fetal_issues_true,
  fetal_issues_false,
  fetal_issues_null,
  SAFE_DIVIDE(fetal_issues_true, total_bills) * 100 as fetal_issues_true_pct,
  
  -- Fetal Tissue
  fetal_tissue_true,
  fetal_tissue_false,
  fetal_tissue_null,
  SAFE_DIVIDE(fetal_tissue_true, total_bills) * 100 as fetal_tissue_true_pct,
  
  -- Incarceration
  incarceration_true,
  incarceration_false,
  incarceration_null,
  SAFE_DIVIDE(incarceration_true, total_bills) * 100 as incarceration_true_pct,
  
  -- Period Products
  period_products_true,
  period_products_false,
  period_products_null,
  SAFE_DIVIDE(period_products_true, total_bills) * 100 as period_products_true_pct,
  
  -- STIs
  stis_true,
  stis_false,
  stis_null,
  SAFE_DIVIDE(stis_true, total_bills) * 100 as stis_true_pct
  
FROM policy_categories
ORDER BY state, data_year;

-- 2. BILL STATUS ANALYTICS BY STATE AND YEAR (MATERIALIZED TABLE FOR LOOKER PERFORMANCE)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.state_year_status_analytics` AS
WITH status_counts AS (
  SELECT 
    state,
    data_year,
    -- Status Counts (these should only be TRUE/FALSE, not NULL)
    COUNTIF(introduced IS TRUE) as introduced_count,
    COUNTIF(seriously_considered IS TRUE) as seriously_considered_count,
    COUNTIF(passed_first_chamber IS TRUE) as passed_first_chamber_count,
    COUNTIF(passed_second_chamber IS TRUE) as passed_second_chamber_count,
    COUNTIF(enacted IS TRUE) as enacted_count,
    COUNTIF(vetoed IS TRUE) as vetoed_count,
    COUNTIF(dead IS TRUE) as dead_count,
    COUNTIF(pending IS TRUE) as pending_count,
    
    -- Total bills for reference
    COUNT(*) as total_bills
    
  FROM `{{ project_id }}.{{ dataset_id }}.all_historical_bills_materialized`
  GROUP BY state, data_year
)
SELECT 
  state,
  data_year, 
  total_bills,
  
  -- Counts
  introduced_count,
  seriously_considered_count,
  passed_first_chamber_count,
  passed_second_chamber_count, 
  enacted_count,
  vetoed_count,
  dead_count,
  pending_count,
  
  -- Percentages
  SAFE_DIVIDE(introduced_count, total_bills) * 100 as introduced_pct,
  SAFE_DIVIDE(seriously_considered_count, total_bills) * 100 as seriously_considered_pct,
  SAFE_DIVIDE(passed_first_chamber_count, total_bills) * 100 as passed_first_chamber_pct,
  SAFE_DIVIDE(passed_second_chamber_count, total_bills) * 100 as passed_second_chamber_pct,
  SAFE_DIVIDE(enacted_count, total_bills) * 100 as enacted_pct,
  SAFE_DIVIDE(vetoed_count, total_bills) * 100 as vetoed_pct,
  SAFE_DIVIDE(dead_count, total_bills) * 100 as dead_pct,
  SAFE_DIVIDE(pending_count, total_bills) * 100 as pending_pct,
  
  -- Success Metrics
  SAFE_DIVIDE(enacted_count, GREATEST(introduced_count, 1)) * 100 as success_rate_pct,
  SAFE_DIVIDE(enacted_count + vetoed_count, GREATEST(introduced_count, 1)) * 100 as completion_rate_pct
  
FROM status_counts
ORDER BY state, data_year;

-- 3. INTENT ANALYTICS BY STATE AND YEAR (MATERIALIZED TABLE FOR LOOKER PERFORMANCE)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.state_year_intent_analytics` AS
WITH intent_counts AS (
  SELECT 
    state,
    data_year,
    -- Intent Counts (can be NULL for early years)
    COUNTIF(positive IS TRUE) as positive_true,
    COUNTIF(positive IS FALSE) as positive_false,
    COUNTIF(positive IS NULL) as positive_null,
    
    COUNTIF(neutral IS TRUE) as neutral_true,
    COUNTIF(neutral IS FALSE) as neutral_false,
    COUNTIF(neutral IS NULL) as neutral_null,
    
    COUNTIF(restrictive IS TRUE) as restrictive_true,
    COUNTIF(restrictive IS FALSE) as restrictive_false,
    COUNTIF(restrictive IS NULL) as restrictive_null,
    
    -- Bills where intent was actually tracked (not NULL)
    COUNTIF(positive IS NOT NULL OR neutral IS NOT NULL OR restrictive IS NOT NULL) as intent_tracked_bills,
    
    -- Total bills for reference
    COUNT(*) as total_bills
    
  FROM `{{ project_id }}.{{ dataset_id }}.all_historical_bills_materialized`
  GROUP BY state, data_year
)
SELECT 
  state,
  data_year,
  total_bills,
  intent_tracked_bills,
  
  -- Raw counts
  positive_true,
  positive_false,
  positive_null,
  neutral_true,
  neutral_false,
  neutral_null,
  restrictive_true,
  restrictive_false, 
  restrictive_null,
  
  -- Percentages of all bills
  SAFE_DIVIDE(positive_true, total_bills) * 100 as positive_pct_all,
  SAFE_DIVIDE(neutral_true, total_bills) * 100 as neutral_pct_all,
  SAFE_DIVIDE(restrictive_true, total_bills) * 100 as restrictive_pct_all,
  
  -- Percentages of bills where intent was tracked
  SAFE_DIVIDE(positive_true, GREATEST(intent_tracked_bills, 1)) * 100 as positive_pct_tracked,
  SAFE_DIVIDE(neutral_true, GREATEST(intent_tracked_bills, 1)) * 100 as neutral_pct_tracked,
  SAFE_DIVIDE(restrictive_true, GREATEST(intent_tracked_bills, 1)) * 100 as restrictive_pct_tracked,
  
  -- Data availability
  SAFE_DIVIDE(intent_tracked_bills, total_bills) * 100 as intent_tracking_coverage_pct
  
FROM intent_counts
ORDER BY state, data_year;

-- 4. BILL TYPE ANALYTICS BY STATE AND YEAR (MATERIALIZED TABLE FOR LOOKER PERFORMANCE)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.state_year_billtype_analytics` AS
WITH billtype_counts AS (
  SELECT 
    state,
    data_year,
    -- Bill Type Counts (can be NULL for early years)
    COUNTIF(legislation IS TRUE) as legislation_true,
    COUNTIF(legislation IS FALSE) as legislation_false,
    COUNTIF(legislation IS NULL) as legislation_null,
    
    COUNTIF(resolution IS TRUE) as resolution_true,
    COUNTIF(resolution IS FALSE) as resolution_false,
    COUNTIF(resolution IS NULL) as resolution_null,
    
    COUNTIF(ballot_initiative IS TRUE) as ballot_initiative_true,
    COUNTIF(ballot_initiative IS FALSE) as ballot_initiative_false,
    COUNTIF(ballot_initiative IS NULL) as ballot_initiative_null,
    
    COUNTIF(constitutional_amendment IS TRUE) as constitutional_amendment_true,
    COUNTIF(constitutional_amendment IS FALSE) as constitutional_amendment_false,
    COUNTIF(constitutional_amendment IS NULL) as constitutional_amendment_null,
    
    -- Bills where type was tracked
    COUNTIF(legislation IS NOT NULL OR resolution IS NOT NULL OR 
            ballot_initiative IS NOT NULL OR constitutional_amendment IS NOT NULL) as type_tracked_bills,
    
    -- Total bills for reference
    COUNT(*) as total_bills
    
  FROM `{{ project_id }}.{{ dataset_id }}.all_historical_bills_materialized`
  GROUP BY state, data_year
)
SELECT 
  state,
  data_year,
  total_bills,
  type_tracked_bills,
  
  -- Raw counts
  legislation_true,
  legislation_false,
  legislation_null,
  resolution_true,
  resolution_false,
  resolution_null,
  ballot_initiative_true,
  ballot_initiative_false,
  ballot_initiative_null,
  constitutional_amendment_true,
  constitutional_amendment_false,
  constitutional_amendment_null,
  
  -- Percentages of all bills
  SAFE_DIVIDE(legislation_true, total_bills) * 100 as legislation_pct_all,
  SAFE_DIVIDE(resolution_true, total_bills) * 100 as resolution_pct_all,
  SAFE_DIVIDE(ballot_initiative_true, total_bills) * 100 as ballot_initiative_pct_all,
  SAFE_DIVIDE(constitutional_amendment_true, total_bills) * 100 as constitutional_amendment_pct_all,
  
  -- Percentages of bills where type was tracked
  SAFE_DIVIDE(legislation_true, GREATEST(type_tracked_bills, 1)) * 100 as legislation_pct_tracked,
  SAFE_DIVIDE(resolution_true, GREATEST(type_tracked_bills, 1)) * 100 as resolution_pct_tracked,
  SAFE_DIVIDE(ballot_initiative_true, GREATEST(type_tracked_bills, 1)) * 100 as ballot_initiative_pct_tracked,
  SAFE_DIVIDE(constitutional_amendment_true, GREATEST(type_tracked_bills, 1)) * 100 as constitutional_amendment_pct_tracked,
  
  -- Data availability
  SAFE_DIVIDE(type_tracked_bills, total_bills) * 100 as type_tracking_coverage_pct
  
FROM billtype_counts
ORDER BY state, data_year;

-- 5. COMPREHENSIVE TIME SERIES TABLE (ALL METRICS - OPTIMIZED FOR LOOKER)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.comprehensive_time_series` AS
SELECT 
  p.state,
  p.data_year,
  p.total_bills,
  
  -- Top policy areas (counts)
  p.abortion_true,
  p.contraception_true,
  p.minors_true,
  p.insurance_true,
  p.appropriations_true,
  
  -- Top policy areas (percentages)
  p.abortion_true_pct,
  p.contraception_true_pct,
  p.minors_true_pct,
  p.insurance_true_pct,
  p.appropriations_true_pct,
  
  -- Status metrics
  s.introduced_count,
  s.enacted_count,
  s.success_rate_pct,
  
  -- Intent metrics (when available)
  i.positive_true,
  i.neutral_true,
  i.restrictive_true,
  i.intent_tracking_coverage_pct,
  
  -- Bill type metrics (when available)
  b.legislation_true,
  b.resolution_true,
  b.type_tracking_coverage_pct
  
FROM `{{ project_id }}.{{ dataset_id }}.state_year_policy_analytics` p
LEFT JOIN `{{ project_id }}.{{ dataset_id }}.state_year_status_analytics` s
  ON p.state = s.state AND p.data_year = s.data_year
LEFT JOIN `{{ project_id }}.{{ dataset_id }}.state_year_intent_analytics` i
  ON p.state = i.state AND p.data_year = i.data_year  
LEFT JOIN `{{ project_id }}.{{ dataset_id }}.state_year_billtype_analytics` b
  ON p.state = b.state AND p.data_year = b.data_year
ORDER BY p.state, p.data_year;

-- 6. NATIONAL TIME SERIES TABLE (AGGREGATED ACROSS STATES - OPTIMIZED FOR LOOKER)
CREATE OR REPLACE TABLE `{{ project_id }}.{{ dataset_id }}.national_time_series` AS
SELECT 
  data_year,
  
  -- Total bills nationally
  SUM(total_bills) as total_bills_national,
  COUNT(DISTINCT state) as states_with_data,
  
  -- Policy area totals
  SUM(abortion_true) as abortion_bills_national,
  SUM(contraception_true) as contraception_bills_national,
  SUM(minors_true) as minors_bills_national,
  SUM(insurance_true) as insurance_bills_national,
  SUM(appropriations_true) as appropriations_bills_national,
  
  -- Status totals
  SUM(introduced_count) as introduced_bills_national,
  SUM(enacted_count) as enacted_bills_national,
  SAFE_DIVIDE(SUM(enacted_count), SUM(introduced_count)) * 100 as national_success_rate_pct,
  
  -- Intent totals (when tracked)
  SUM(positive_true) as positive_bills_national,
  SUM(neutral_true) as neutral_bills_national,
  SUM(restrictive_true) as restrictive_bills_national,
  
  -- Bill type totals (when tracked)
  SUM(legislation_true) as legislation_bills_national,
  SUM(resolution_true) as resolution_bills_national,
  
  -- Data coverage metrics
  AVG(intent_tracking_coverage_pct) as avg_intent_coverage_pct,
  AVG(type_tracking_coverage_pct) as avg_type_coverage_pct
  
FROM `{{ project_id }}.{{ dataset_id }}.comprehensive_time_series`
GROUP BY data_year
ORDER BY data_year;