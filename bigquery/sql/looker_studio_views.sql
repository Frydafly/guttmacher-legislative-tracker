-- Looker Studio Optimized Views
-- These views are specifically designed for optimal performance in Looker Studio
-- Run these after the main pipeline completes

-- =====================================================================
-- Main Dashboard View - Primary data source for Looker Studio
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_main_dashboard` AS
SELECT 
    -- Primary identifiers
    bill_id,
    CONCAT(state, '-', bill_number, '-', CAST(data_year AS STRING)) as unique_bill_key,
    
    -- Geographic and temporal dimensions
    state as state_code,
    CASE state
        WHEN 'AL' THEN 'Alabama'
        WHEN 'AK' THEN 'Alaska'
        WHEN 'AZ' THEN 'Arizona'
        WHEN 'AR' THEN 'Arkansas'
        WHEN 'CA' THEN 'California'
        -- Add all other states as needed
        ELSE state
    END as state_name,
    
    data_year,
    CAST(data_year AS STRING) as data_year_str,  -- For categorical filtering
    
    -- Bill information
    bill_type,
    bill_number,
    description,
    
    -- Status dimensions
    status_category,
    bill_stage,
    current_bill_status as detailed_status,
    
    -- Intent flags (boolean for easy filtering)
    is_positive,
    is_restrictive, 
    is_neutral,
    
    -- Intent as categorical dimension
    CASE 
        WHEN is_positive AND is_restrictive THEN 'Mixed'
        WHEN is_positive THEN 'Positive'
        WHEN is_restrictive THEN 'Restrictive'
        ELSE 'Neutral'
    END as intent_category,
    
    -- Date dimensions
    introduction_date,
    enacted_date,
    vetoed_date,
    last_action,
    
    -- Date components for time-based analysis
    intro_year,
    intro_month,
    CASE intro_month
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
    END as intro_month_name,
    
    EXTRACT(QUARTER FROM introduction_date) as intro_quarter,
    
    -- Outcome flags
    CASE WHEN enacted_date IS NOT NULL THEN TRUE ELSE FALSE END as is_enacted,
    CASE WHEN vetoed_date IS NOT NULL THEN TRUE ELSE FALSE END as is_vetoed,
    
    -- Time to action (useful for analysis)
    DATE_DIFF(enacted_date, introduction_date, DAY) as days_to_enactment,
    DATE_DIFF(vetoed_date, introduction_date, DAY) as days_to_veto,
    DATE_DIFF(last_action, introduction_date, DAY) as days_since_introduction,
    
    -- Data provenance
    data_source,
    last_updated
    
FROM `{project_id}.{dataset_id}.analytics_bills_view`
WHERE state IS NOT NULL 
  AND bill_number IS NOT NULL
  AND data_year BETWEEN 2000 AND 2030;  -- Reasonable data range

-- =====================================================================
-- Summary Statistics for High-Level KPIs
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_summary_kpis` AS
SELECT 
    -- Aggregation dimensions
    data_year,
    state_code,
    state_name,
    intent_category,
    status_category,
    
    -- Core metrics
    COUNT(*) as total_bills,
    COUNT(CASE WHEN is_enacted THEN 1 END) as enacted_bills,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as vetoed_bills,
    COUNT(CASE WHEN is_positive THEN 1 END) as positive_bills,
    COUNT(CASE WHEN is_restrictive THEN 1 END) as restrictive_bills,
    
    -- Calculated percentages
    ROUND(COUNT(CASE WHEN is_enacted THEN 1 END) * 100.0 / COUNT(*), 1) as enactment_rate,
    ROUND(COUNT(CASE WHEN is_vetoed THEN 1 END) * 100.0 / COUNT(*), 1) as veto_rate,
    ROUND(COUNT(CASE WHEN is_positive THEN 1 END) * 100.0 / COUNT(*), 1) as positive_rate,
    ROUND(COUNT(CASE WHEN is_restrictive THEN 1 END) * 100.0 / COUNT(*), 1) as restrictive_rate,
    
    -- Average processing times
    ROUND(AVG(days_to_enactment), 1) as avg_days_to_enactment,
    ROUND(AVG(days_to_veto), 1) as avg_days_to_veto,
    
    -- Data freshness
    MAX(last_updated) as data_last_updated
    
FROM `{project_id}.{dataset_id}.looker_main_dashboard`
GROUP BY data_year, state_code, state_name, intent_category, status_category;

-- =====================================================================
-- Time Series Data for Trending Analysis
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_time_series` AS
SELECT 
    -- Time dimensions
    data_year,
    intro_year,
    intro_month,
    intro_month_name,
    intro_quarter,
    CONCAT(CAST(intro_year AS STRING), '-', 
           LPAD(CAST(intro_month AS STRING), 2, '0')) as year_month,
    
    -- Geographic dimension
    state_code,
    state_name,
    
    -- Metrics by time period
    COUNT(*) as bills_introduced,
    COUNT(CASE WHEN is_enacted THEN 1 END) as bills_enacted,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as bills_vetoed,
    COUNT(CASE WHEN is_positive THEN 1 END) as positive_bills,
    COUNT(CASE WHEN is_restrictive THEN 1 END) as restrictive_bills,
    
    -- Rolling averages (3-month)
    AVG(COUNT(*)) OVER (
        PARTITION BY state_code 
        ORDER BY intro_year, intro_month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as bills_3month_avg,
    
    -- Year-over-year comparisons
    COUNT(*) - LAG(COUNT(*), 12) OVER (
        PARTITION BY state_code, intro_month 
        ORDER BY intro_year
    ) as bills_yoy_change,
    
    -- Cumulative totals by year
    SUM(COUNT(*)) OVER (
        PARTITION BY state_code, intro_year 
        ORDER BY intro_month
    ) as bills_ytd
    
FROM `{project_id}.{dataset_id}.looker_main_dashboard`
WHERE intro_year IS NOT NULL AND intro_month IS NOT NULL
GROUP BY 
    data_year, intro_year, intro_month, intro_month_name, intro_quarter,
    state_code, state_name
ORDER BY intro_year DESC, intro_month DESC, state_code;

-- =====================================================================
-- Geographic Analysis View
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_geographic_analysis` AS
SELECT 
    state_code,
    state_name,
    
    -- Overall statistics
    COUNT(*) as total_bills_all_years,
    COUNT(DISTINCT data_year) as years_with_data,
    MIN(data_year) as first_year,
    MAX(data_year) as last_year,
    
    -- By intent
    COUNT(CASE WHEN is_positive THEN 1 END) as total_positive,
    COUNT(CASE WHEN is_restrictive THEN 1 END) as total_restrictive,
    COUNT(CASE WHEN is_neutral THEN 1 END) as total_neutral,
    
    -- By outcome
    COUNT(CASE WHEN is_enacted THEN 1 END) as total_enacted,
    COUNT(CASE WHEN is_vetoed THEN 1 END) as total_vetoed,
    
    -- Rates
    ROUND(COUNT(CASE WHEN is_positive THEN 1 END) * 100.0 / COUNT(*), 1) as positive_rate,
    ROUND(COUNT(CASE WHEN is_restrictive THEN 1 END) * 100.0 / COUNT(*), 1) as restrictive_rate,
    ROUND(COUNT(CASE WHEN is_enacted THEN 1 END) * 100.0 / COUNT(*), 1) as enactment_rate,
    
    -- Activity level categorization
    CASE 
        WHEN COUNT(*) >= 100 THEN 'High Activity'
        WHEN COUNT(*) >= 50 THEN 'Medium Activity'
        WHEN COUNT(*) >= 20 THEN 'Low Activity'
        ELSE 'Very Low Activity'
    END as activity_level,
    
    -- Legislative climate
    CASE 
        WHEN COUNT(CASE WHEN is_positive THEN 1 END) > COUNT(CASE WHEN is_restrictive THEN 1 END) THEN 'Positive-leaning'
        WHEN COUNT(CASE WHEN is_restrictive THEN 1 END) > COUNT(CASE WHEN is_positive THEN 1 END) THEN 'Restrictive-leaning'
        ELSE 'Balanced'
    END as legislative_climate
    
FROM `{project_id}.{dataset_id}.looker_main_dashboard`
GROUP BY state_code, state_name
ORDER BY total_bills_all_years DESC;

-- =====================================================================
-- Bill Details View (for drill-down analysis)
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_bill_details` AS
SELECT 
    -- All fields from main dashboard
    *,
    
    -- Additional detail fields
    CASE 
        WHEN days_to_enactment IS NOT NULL AND days_to_enactment <= 30 THEN 'Fast Track (≤30 days)'
        WHEN days_to_enactment IS NOT NULL AND days_to_enactment <= 90 THEN 'Standard (31-90 days)'
        WHEN days_to_enactment IS NOT NULL AND days_to_enactment <= 180 THEN 'Slow (91-180 days)'
        WHEN days_to_enactment IS NOT NULL THEN 'Very Slow (>180 days)'
        ELSE 'Not Enacted'
    END as enactment_speed,
    
    -- Legislative session timing
    CASE 
        WHEN intro_month IN (1, 2, 3) THEN 'Q1 - Early Session'
        WHEN intro_month IN (4, 5, 6) THEN 'Q2 - Mid Session'
        WHEN intro_month IN (7, 8, 9) THEN 'Q3 - Late Session'
        WHEN intro_month IN (10, 11, 12) THEN 'Q4 - Special/Interim'
        ELSE 'Unknown'
    END as session_timing,
    
    -- Bill complexity indicators
    CASE 
        WHEN LENGTH(description) > 500 THEN 'Complex'
        WHEN LENGTH(description) > 200 THEN 'Standard'
        WHEN LENGTH(description) > 0 THEN 'Simple'
        ELSE 'No Description'
    END as bill_complexity
    
FROM `{project_id}.{dataset_id}.looker_main_dashboard`;

-- =====================================================================
-- Data Quality Monitor View
-- =====================================================================
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.looker_data_quality` AS
SELECT 
    data_year,
    state_code,
    
    -- Record counts
    COUNT(*) as total_records,
    
    -- Completeness metrics
    COUNT(CASE WHEN bill_number IS NOT NULL THEN 1 END) as bills_with_number,
    COUNT(CASE WHEN description IS NOT NULL AND LENGTH(description) > 0 THEN 1 END) as bills_with_description,
    COUNT(CASE WHEN introduction_date IS NOT NULL THEN 1 END) as bills_with_intro_date,
    COUNT(CASE WHEN status_category != 'Unknown' THEN 1 END) as bills_with_status,
    
    -- Quality percentages
    ROUND(COUNT(CASE WHEN bill_number IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 1) as bill_number_completeness,
    ROUND(COUNT(CASE WHEN description IS NOT NULL AND LENGTH(description) > 0 THEN 1 END) * 100.0 / COUNT(*), 1) as description_completeness,
    ROUND(COUNT(CASE WHEN introduction_date IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 1) as intro_date_completeness,
    
    -- Data freshness
    MAX(last_updated) as last_update_time,
    DATE_DIFF(CURRENT_DATE(), MAX(DATE(last_updated)), DAY) as days_since_update
    
FROM `{project_id}.{dataset_id}.looker_main_dashboard`
GROUP BY data_year, state_code
ORDER BY data_year DESC, state_code;