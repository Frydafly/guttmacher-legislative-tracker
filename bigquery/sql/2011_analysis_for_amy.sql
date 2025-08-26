-- Analysis of 2011 Legislative Data for Amy Littlefield from The Nation
-- Question: How many of the 1,100 reproductive health provisions were restrictive vs protective?

-- Create a view summarizing 2011 data by intent
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.analysis_2011_intent_breakdown` AS
WITH bill_analysis AS (
    SELECT 
        state,
        bill_number,
        bill_type,
        summary,
        positive_flag,
        negative_flag,
        neutral_flag,
        enacted_flag,
        CASE 
            WHEN negative_flag = TRUE THEN 'Restrictive'
            WHEN positive_flag = TRUE THEN 'Protective'
            WHEN neutral_flag = TRUE THEN 'Neutral'
            ELSE 'Unclassified'
        END as intent_classification,
        -- Check for bills with multiple classifications
        CASE 
            WHEN positive_flag = TRUE AND negative_flag = TRUE THEN 'Mixed'
            WHEN positive_flag = TRUE THEN 'Protective Only'
            WHEN negative_flag = TRUE THEN 'Restrictive Only'
            WHEN neutral_flag = TRUE THEN 'Neutral Only'
            ELSE 'None'
        END as classification_type
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.historical_bills_2011`
)
SELECT 
    '2011 Legislative Provisions Analysis' as report_title,
    COUNT(*) as total_provisions,
    
    -- Intent breakdown
    SUM(CASE WHEN intent_classification = 'Restrictive' THEN 1 ELSE 0 END) as restrictive_count,
    ROUND(SUM(CASE WHEN intent_classification = 'Restrictive' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as restrictive_pct,
    
    SUM(CASE WHEN intent_classification = 'Protective' THEN 1 ELSE 0 END) as protective_count,
    ROUND(SUM(CASE WHEN intent_classification = 'Protective' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as protective_pct,
    
    SUM(CASE WHEN intent_classification = 'Neutral' THEN 1 ELSE 0 END) as neutral_count,
    ROUND(SUM(CASE WHEN intent_classification = 'Neutral' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as neutral_pct,
    
    -- Enacted breakdown
    SUM(CASE WHEN enacted_flag = TRUE THEN 1 ELSE 0 END) as total_enacted,
    SUM(CASE WHEN enacted_flag = TRUE AND intent_classification = 'Restrictive' THEN 1 ELSE 0 END) as enacted_restrictive,
    SUM(CASE WHEN enacted_flag = TRUE AND intent_classification = 'Protective' THEN 1 ELSE 0 END) as enacted_protective,
    
    -- Mixed classifications
    SUM(CASE WHEN classification_type = 'Mixed' THEN 1 ELSE 0 END) as bills_with_mixed_intent,
    
    -- Summary for Amy
    CONCAT(
        'Of the ', COUNT(*), ' reproductive health provisions tracked in 2011: ',
        SUM(CASE WHEN intent_classification = 'Restrictive' THEN 1 ELSE 0 END), ' (', 
        ROUND(SUM(CASE WHEN intent_classification = 'Restrictive' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1), 
        '%) were restrictive, ',
        SUM(CASE WHEN intent_classification = 'Protective' THEN 1 ELSE 0 END), ' (',
        ROUND(SUM(CASE WHEN intent_classification = 'Protective' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1),
        '%) were protective.'
    ) as summary_for_amy
FROM bill_analysis;

-- Also create a detailed breakdown by state
CREATE OR REPLACE VIEW `guttmacher-legislative-tracker.legislative_tracker_historical.analysis_2011_by_state` AS
SELECT 
    state,
    COUNT(*) as total_bills,
    SUM(CASE WHEN negative_flag = TRUE THEN 1 ELSE 0 END) as restrictive,
    SUM(CASE WHEN positive_flag = TRUE THEN 1 ELSE 0 END) as protective,
    SUM(CASE WHEN neutral_flag = TRUE THEN 1 ELSE 0 END) as neutral,
    SUM(CASE WHEN enacted_flag = TRUE THEN 1 ELSE 0 END) as enacted
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.historical_bills_2011`
GROUP BY state
ORDER BY total_bills DESC;