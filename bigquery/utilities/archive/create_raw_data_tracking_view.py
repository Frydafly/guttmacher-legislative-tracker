from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("Creating raw data tracking view for dashboard...")
print("=" * 80)

# Create a comprehensive view showing what was actually tracked each year
raw_data_tracking_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.raw_data_tracking_by_year` AS
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Basic data collection (should always be tracked)
  SUM(CASE WHEN state IS NOT NULL THEN 1 ELSE 0 END) as has_state_data,
  SUM(CASE WHEN bill_number IS NOT NULL THEN 1 ELSE 0 END) as has_bill_number_data,
  SUM(CASE WHEN description IS NOT NULL THEN 1 ELSE 0 END) as has_description_data,
  SUM(CASE WHEN history IS NOT NULL THEN 1 ELSE 0 END) as has_history_data,
  
  -- Bill classification evolution
  SUM(CASE WHEN bill_type IS NOT NULL THEN 1 ELSE 0 END) as has_bill_type_data,
  SUM(CASE WHEN internal_summary IS NOT NULL THEN 1 ELSE 0 END) as has_internal_summary_data,
  SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) as has_notes_data,
  SUM(CASE WHEN website_blurb IS NOT NULL THEN 1 ELSE 0 END) as has_website_blurb_data,
  
  -- Date tracking evolution  
  SUM(CASE WHEN introduced_date IS NOT NULL THEN 1 ELSE 0 END) as has_introduced_date_data,
  SUM(CASE WHEN last_action_date IS NOT NULL THEN 1 ELSE 0 END) as has_last_action_date_data,
  SUM(CASE WHEN effective_date IS NOT NULL THEN 1 ELSE 0 END) as has_effective_date_data,
  SUM(CASE WHEN enacted_date IS NOT NULL THEN 1 ELSE 0 END) as has_enacted_date_data,
  
  -- Policy category tracking (NULL = not tracked, TRUE/FALSE = tracked)
  COUNTIF(abortion IS NOT NULL) as tracked_abortion_bills,
  COUNTIF(abortion = TRUE) as marked_abortion_true,
  COUNTIF(contraception IS NOT NULL) as tracked_contraception_bills,
  COUNTIF(contraception = TRUE) as marked_contraception_true,
  COUNTIF(minors IS NOT NULL) as tracked_minors_bills,
  COUNTIF(minors = TRUE) as marked_minors_true,
  COUNTIF(sex_education IS NOT NULL) as tracked_sex_education_bills,
  COUNTIF(sex_education = TRUE) as marked_sex_education_true,
  COUNTIF(insurance IS NOT NULL) as tracked_insurance_bills,
  COUNTIF(insurance = TRUE) as marked_insurance_true,
  COUNTIF(pregnancy IS NOT NULL) as tracked_pregnancy_bills,
  COUNTIF(pregnancy = TRUE) as marked_pregnancy_true,
  COUNTIF(emergency_contraception IS NOT NULL) as tracked_emergency_contraception_bills,
  COUNTIF(emergency_contraception = TRUE) as marked_emergency_contraception_true,
  COUNTIF(appropriations IS NOT NULL) as tracked_appropriations_bills,
  COUNTIF(appropriations = TRUE) as marked_appropriations_true,
  
  -- Status field tracking (modern methodology post-2006)
  COUNTIF(introduced IS NOT NULL) as tracked_introduced_status,
  COUNTIF(introduced = TRUE) as marked_introduced_true,
  COUNTIF(enacted IS NOT NULL) as tracked_enacted_status,
  COUNTIF(enacted = TRUE) as marked_enacted_true,
  COUNTIF(vetoed IS NOT NULL) as tracked_vetoed_status,
  COUNTIF(vetoed = TRUE) as marked_vetoed_true,
  COUNTIF(dead IS NOT NULL) as tracked_dead_status,
  COUNTIF(dead = TRUE) as marked_dead_true,
  COUNTIF(pending IS NOT NULL) as tracked_pending_status,
  COUNTIF(pending = TRUE) as marked_pending_true,
  
  -- Intent classification tracking
  COUNTIF(positive IS NOT NULL) as tracked_positive_intent,
  COUNTIF(positive = TRUE) as marked_positive_true,
  COUNTIF(neutral IS NOT NULL) as tracked_neutral_intent,
  COUNTIF(neutral = TRUE) as marked_neutral_true,
  COUNTIF(restrictive IS NOT NULL) as tracked_restrictive_intent,
  COUNTIF(restrictive = TRUE) as marked_restrictive_true,
  
  -- Emerging policy areas
  COUNTIF(period_products IS NOT NULL) as tracked_period_products_bills,
  COUNTIF(period_products = TRUE) as marked_period_products_true,
  COUNTIF(incarceration IS NOT NULL) as tracked_incarceration_bills,
  COUNTIF(incarceration = TRUE) as marked_incarceration_true,
  
  -- Calculate tracking percentages for key fields
  ROUND(SUM(CASE WHEN bill_type IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as bill_type_tracking_pct,
  ROUND(SUM(CASE WHEN introduced_date IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as introduced_date_tracking_pct,
  ROUND(COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100, 1) as abortion_tracking_pct,
  ROUND(COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100, 1) as contraception_tracking_pct,
  ROUND(COUNTIF(positive IS NOT NULL) / COUNT(*) * 100, 1) as intent_tracking_pct,
  
  -- Calculate marking percentages (when tracked, what % was marked TRUE)
  CASE 
    WHEN COUNTIF(abortion IS NOT NULL) > 0 
    THEN ROUND(COUNTIF(abortion = TRUE) / COUNTIF(abortion IS NOT NULL) * 100, 1)
    ELSE NULL 
  END as abortion_true_rate_when_tracked,
  
  CASE 
    WHEN COUNTIF(contraception IS NOT NULL) > 0 
    THEN ROUND(COUNTIF(contraception = TRUE) / COUNTIF(contraception IS NOT NULL) * 100, 1)
    ELSE NULL 
  END as contraception_true_rate_when_tracked,
  
  CASE 
    WHEN COUNTIF(introduced IS NOT NULL) > 0 
    THEN ROUND(COUNTIF(introduced = TRUE) / COUNTIF(introduced IS NOT NULL) * 100, 1)
    ELSE NULL 
  END as introduced_true_rate_when_tracked,
  
  CASE 
    WHEN COUNTIF(enacted IS NOT NULL) > 0 
    THEN ROUND(COUNTIF(enacted = TRUE) / COUNTIF(enacted IS NOT NULL) * 100, 1)
    ELSE NULL 
  END as enacted_true_rate_when_tracked

FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
GROUP BY data_year
ORDER BY data_year
"""

try:
    print("Creating view: raw_data_tracking_by_year")
    print("This view shows what was actually tracked vs what was marked TRUE each year")
    
    query_job = client.query(raw_data_tracking_sql)
    query_job.result()  # Wait for the query to complete
    
    print("✅ Successfully created view: raw_data_tracking_by_year")
    
    # Get row count and sample data
    sample_query = f"""
    SELECT 
      data_year, 
      total_bills,
      bill_type_tracking_pct,
      introduced_date_tracking_pct,
      abortion_tracking_pct,
      abortion_true_rate_when_tracked,
      contraception_tracking_pct,
      contraception_true_rate_when_tracked
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.raw_data_tracking_by_year`
    WHERE data_year IN (2002, 2006, 2016, 2022)
    ORDER BY data_year
    """
    
    print("\n📊 Sample data from the view:")
    print("Year | Bills | BillType% | IntroDate% | Abortion% | AbortTrue% | Contracept% | ContractTrue%")
    print("-" * 90)
    
    sample_results = client.query(sample_query).result()
    for row in sample_results:
        abortion_true = f"{row.abortion_true_rate_when_tracked:.1f}%" if row.abortion_true_rate_when_tracked else "N/A"
        contraception_true = f"{row.contraception_true_rate_when_tracked:.1f}%" if row.contraception_true_rate_when_tracked else "N/A"
        
        print(f"{row.data_year} | {row.total_bills:4d} | {row.bill_type_tracking_pct:7.1f}% | "
              f"{row.introduced_date_tracking_pct:8.1f}% | {row.abortion_tracking_pct:8.1f}% | "
              f"{abortion_true:8s} | {row.contraception_tracking_pct:9.1f}% | {contraception_true:11s}")
    
    print(f"\n✅ View created successfully!")
    print(f"📍 Location: {os.getenv('GCP_PROJECT_ID')}.{dataset_id}.raw_data_tracking_by_year")
    print(f"🔗 Ready for dashboard integration")
    
except Exception as e:
    print(f"❌ Error creating view: {str(e)}")

print(f"\n{'='*80}")
print("VIEW USAGE GUIDE")
print(f"{'='*80}")

print("""
This view provides two critical metrics for each field:

1. **Tracking %**: What percentage of bills had this field tracked (NOT NULL)
   - 0% = Field didn't exist that year
   - 100% = Field was systematically tracked for all bills

2. **True Rate When Tracked**: Of the bills where the field was tracked, what % were marked TRUE
   - Shows actual activity/marking patterns
   - Only calculated when field was being tracked

Key columns:
- *_tracking_pct: Shows field evolution (when tracking started)
- *_true_rate_when_tracked: Shows marking patterns (when tracked, what was marked TRUE)
- tracked_*_bills: Raw count of bills where field was tracked
- marked_*_true: Raw count of bills marked TRUE

Dashboard Use Cases:
- Line chart: tracking percentages over time (shows when fields were introduced)
- Bar chart: true rates when tracked (shows actual policy activity)
- Heatmap: tracking vs marking patterns
- Table: year-by-year field evolution summary
""")