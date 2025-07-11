from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("Creating field analysis views for dashboard integration...")
print("=" * 80)

# 1. Field Population Analysis by Year
field_population_view_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_population_by_year` AS
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Basic identifier fields
  'state' as field_name, 'Basic Identifier' as field_category,
  COUNTIF(state IS NOT NULL) / COUNT(*) * 100 as populated_pct,
  COUNTIF(state IS NULL) / COUNT(*) * 100 as null_pct,
  'State abbreviation' as field_description
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'bill_number', 'Basic Identifier',
  COUNTIF(bill_number IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(bill_number IS NULL) / COUNT(*) * 100,
  'Bill number/identifier'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'bill_type', 'Basic Identifier',
  COUNTIF(bill_type IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(bill_type IS NULL) / COUNT(*) * 100,
  'Type of legislation'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Text description fields
SELECT 
  data_year, COUNT(*) as total_bills,
  'description', 'Text Field',
  COUNTIF(description IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(description IS NULL) / COUNT(*) * 100,
  'Bill description/title'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'internal_summary', 'Text Field',
  COUNTIF(internal_summary IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(internal_summary IS NULL) / COUNT(*) * 100,
  'Internal summary of bill'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'notes', 'Text Field',
  COUNTIF(notes IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(notes IS NULL) / COUNT(*) * 100,
  'Additional notes'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'history', 'Text Field',
  COUNTIF(history IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(history IS NULL) / COUNT(*) * 100,
  'Legislative history'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Date fields
SELECT 
  data_year, COUNT(*) as total_bills,
  'introduced_date', 'Date Field',
  COUNTIF(introduced_date IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(introduced_date IS NULL) / COUNT(*) * 100,
  'Date bill was introduced'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'last_action_date', 'Date Field',
  COUNTIF(last_action_date IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(last_action_date IS NULL) / COUNT(*) * 100,
  'Date of most recent action'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'effective_date', 'Date Field',
  COUNTIF(effective_date IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(effective_date IS NULL) / COUNT(*) * 100,
  'Date bill takes effect'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'enacted_date', 'Date Field',
  COUNTIF(enacted_date IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(enacted_date IS NULL) / COUNT(*) * 100,
  'Date bill was enacted'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Status fields (should be 100% populated)
SELECT 
  data_year, COUNT(*) as total_bills,
  'introduced', 'Status Field',
  COUNTIF(introduced IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(introduced IS NULL) / COUNT(*) * 100,
  'Bill was introduced'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'enacted', 'Status Field',
  COUNTIF(enacted IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(enacted IS NULL) / COUNT(*) * 100,
  'Bill was enacted'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'dead', 'Status Field',
  COUNTIF(dead IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(dead IS NULL) / COUNT(*) * 100,
  'Bill failed/died'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Policy category fields
SELECT 
  data_year, COUNT(*) as total_bills,
  'abortion', 'Policy Category',
  COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(abortion IS NULL) / COUNT(*) * 100,
  'Abortion-related bills'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'contraception', 'Policy Category',
  COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(contraception IS NULL) / COUNT(*) * 100,
  'Contraception-related bills'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*) as total_bills,
  'minors', 'Policy Category',
  COUNTIF(minors IS NOT NULL) / COUNT(*) * 100,
  COUNTIF(minors IS NULL) / COUNT(*) * 100,
  'Bills affecting minors'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

ORDER BY data_year, field_category, field_name
"""

# 2. Field TRUE/FALSE/NULL Progression View
field_progression_view_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_true_false_progression` AS
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Status fields with TRUE/FALSE breakdown
  'introduced' as field_name,
  'Status Field' as field_category,
  COUNTIF(introduced = TRUE) as true_count,
  COUNTIF(introduced = FALSE) as false_count,
  COUNTIF(introduced IS NULL) as null_count,
  COUNTIF(introduced = TRUE) / COUNT(*) * 100 as true_pct,
  COUNTIF(introduced = FALSE) / COUNT(*) * 100 as false_pct,
  COUNTIF(introduced IS NULL) / COUNT(*) * 100 as null_pct,
  'Bill was introduced in legislature' as field_description
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'enacted', 'Status Field',
  COUNTIF(enacted = TRUE), COUNTIF(enacted = FALSE), COUNTIF(enacted IS NULL),
  COUNTIF(enacted = TRUE) / COUNT(*) * 100,
  COUNTIF(enacted = FALSE) / COUNT(*) * 100,
  COUNTIF(enacted IS NULL) / COUNT(*) * 100,
  'Bill became law'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'dead', 'Status Field',
  COUNTIF(dead = TRUE), COUNTIF(dead = FALSE), COUNTIF(dead IS NULL),
  COUNTIF(dead = TRUE) / COUNT(*) * 100,
  COUNTIF(dead = FALSE) / COUNT(*) * 100,
  COUNTIF(dead IS NULL) / COUNT(*) * 100,
  'Bill failed/died'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'pending', 'Status Field',
  COUNTIF(pending = TRUE), COUNTIF(pending = FALSE), COUNTIF(pending IS NULL),
  COUNTIF(pending = TRUE) / COUNT(*) * 100,
  COUNTIF(pending = FALSE) / COUNT(*) * 100,
  COUNTIF(pending IS NULL) / COUNT(*) * 100,
  'Bill is still active'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Policy categories
SELECT 
  data_year, COUNT(*),
  'abortion', 'Policy Category',
  COUNTIF(abortion = TRUE), COUNTIF(abortion = FALSE), COUNTIF(abortion IS NULL),
  COUNTIF(abortion = TRUE) / COUNT(*) * 100,
  COUNTIF(abortion = FALSE) / COUNT(*) * 100,
  COUNTIF(abortion IS NULL) / COUNT(*) * 100,
  'Abortion-related bills'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'contraception', 'Policy Category',
  COUNTIF(contraception = TRUE), COUNTIF(contraception = FALSE), COUNTIF(contraception IS NULL),
  COUNTIF(contraception = TRUE) / COUNT(*) * 100,
  COUNTIF(contraception = FALSE) / COUNT(*) * 100,
  COUNTIF(contraception IS NULL) / COUNT(*) * 100,
  'Contraception-related bills'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'minors', 'Policy Category',
  COUNTIF(minors = TRUE), COUNTIF(minors = FALSE), COUNTIF(minors IS NULL),
  COUNTIF(minors = TRUE) / COUNT(*) * 100,
  COUNTIF(minors = FALSE) / COUNT(*) * 100,
  COUNTIF(minors IS NULL) / COUNT(*) * 100,
  'Bills affecting minors'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

-- Intent fields
SELECT 
  data_year, COUNT(*),
  'positive', 'Intent Classification',
  COUNTIF(positive = TRUE), COUNTIF(positive = FALSE), COUNTIF(positive IS NULL),
  COUNTIF(positive = TRUE) / COUNT(*) * 100,
  COUNTIF(positive = FALSE) / COUNT(*) * 100,
  COUNTIF(positive IS NULL) / COUNT(*) * 100,
  'Pro-reproductive rights bills'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

UNION ALL

SELECT 
  data_year, COUNT(*),
  'restrictive', 'Intent Classification',
  COUNTIF(restrictive = TRUE), COUNTIF(restrictive = FALSE), COUNTIF(restrictive IS NULL),
  COUNTIF(restrictive = TRUE) / COUNT(*) * 100,
  COUNTIF(restrictive = FALSE) / COUNT(*) * 100,
  COUNTIF(restrictive IS NULL) / COUNT(*) * 100,
  'Bills restricting reproductive rights'
FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year

ORDER BY data_year, field_category, field_name
"""

# 3. Data Quality Summary View
data_quality_summary_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.data_quality_summary` AS
WITH field_stats AS (
  SELECT 
    field_name,
    field_category,
    field_description,
    COUNT(DISTINCT data_year) as years_tracked,
    AVG(populated_pct) as avg_population_pct,
    MIN(populated_pct) as min_population_pct,
    MAX(populated_pct) as max_population_pct,
    STDDEV(populated_pct) as stddev_population_pct,
    CASE 
      WHEN MIN(populated_pct) >= 99 THEN 'Excellent'
      WHEN MIN(populated_pct) >= 90 THEN 'Good' 
      WHEN MIN(populated_pct) >= 70 THEN 'Moderate'
      WHEN MIN(populated_pct) >= 40 THEN 'Poor'
      ELSE 'Very Poor'
    END as quality_rating,
    CASE
      WHEN STDDEV(populated_pct) < 5 THEN 'Very Stable'
      WHEN STDDEV(populated_pct) < 15 THEN 'Stable'
      WHEN STDDEV(populated_pct) < 30 THEN 'Variable'
      ELSE 'Highly Variable'
    END as consistency_rating
  FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_population_by_year`
  GROUP BY field_name, field_category, field_description
)
SELECT 
  *,
  CASE 
    WHEN quality_rating = 'Excellent' AND consistency_rating IN ('Very Stable', 'Stable') THEN 'Ideal for Analysis'
    WHEN quality_rating IN ('Excellent', 'Good') THEN 'Good for Analysis'
    WHEN quality_rating = 'Moderate' THEN 'Use with Caution'
    ELSE 'Problematic for Analysis'
  END as analysis_recommendation
FROM field_stats
ORDER BY 
  CASE field_category 
    WHEN 'Status Field' THEN 1 
    WHEN 'Policy Category' THEN 2
    WHEN 'Intent Classification' THEN 3
    WHEN 'Basic Identifier' THEN 4
    WHEN 'Date Field' THEN 5
    WHEN 'Text Field' THEN 6
    ELSE 7
  END,
  field_name
"""

# Create the views
views_to_create = [
    ("field_population_by_year", field_population_view_sql, "Field population rates by year for all field types"),
    ("field_true_false_progression", field_progression_view_sql, "TRUE/FALSE/NULL progression for boolean fields"),
    ("data_quality_summary", data_quality_summary_sql, "Summary of data quality ratings for all fields")
]

for view_name, sql, description in views_to_create:
    try:
        print(f"\nCreating view: {view_name}")
        print(f"Description: {description}")
        
        query_job = client.query(sql)
        query_job.result()  # Wait for the query to complete
        
        print(f"✅ Successfully created view: {view_name}")
        
        # Get row count
        count_query = f"SELECT COUNT(*) as row_count FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.{view_name}`"
        count_result = client.query(count_query).result()
        for row in count_result:
            print(f"   📊 Rows: {row.row_count:,}")
            
    except Exception as e:
        print(f"❌ Error creating view {view_name}: {str(e)}")

print(f"\n{'='*80}")
print("DASHBOARD INTEGRATION GUIDE")
print(f"{'='*80}")

print("""
The following views are now available for your dashboard:

1. 📊 field_population_by_year
   - Use for: Time series charts showing field population over time
   - Key columns: data_year, field_name, field_category, populated_pct, null_pct
   - Best for: Line charts, heatmaps showing data quality evolution

2. 📊 field_true_false_progression  
   - Use for: Analyzing TRUE/FALSE patterns for boolean fields
   - Key columns: data_year, field_name, true_pct, false_pct, null_pct
   - Best for: Stacked bar charts, trend analysis for policy categories

3. 📊 data_quality_summary
   - Use for: Overall data quality assessment
   - Key columns: field_name, quality_rating, consistency_rating, analysis_recommendation
   - Best for: Summary tables, quality scorecards

Dashboard Chart Suggestions:
- Line chart: field_population_by_year (x: data_year, y: populated_pct, color: field_name)
- Heatmap: field_population_by_year (x: data_year, y: field_name, color: populated_pct)
- Bar chart: data_quality_summary (x: field_name, y: avg_population_pct, color: quality_rating)
- Stacked area: field_true_false_progression for abortion bills (x: data_year, y: true_pct)
""")

print(f"\n✅ All field analysis views created successfully!")
print(f"📍 Dataset: {os.getenv('GCP_PROJECT_ID')}.{dataset_id}")
print(f"🔗 Ready for Looker Studio integration")