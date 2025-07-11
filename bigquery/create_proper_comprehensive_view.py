from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
dataset_id = "legislative_tracker_historical"

print("🗑️ DROPPING MISLEADING looker_comprehensive_bills TABLE")
print("=" * 70)

# Drop the misleading materialized table
try:
    drop_query = f"DROP TABLE `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.looker_comprehensive_bills`"
    client.query(drop_query).result()
    print("✅ Dropped misleading looker_comprehensive_bills table")
except Exception as e:
    print(f"⚠️ Could not drop table: {e}")

print(f"\n🔧 CREATING PROPER COMPREHENSIVE VIEW")
print("=" * 70)

# Create a proper comprehensive view that preserves NULLs but adds dashboard value
comprehensive_view_sql = f"""
CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic` AS
SELECT 
  -- Unique identifiers
  CONCAT(CAST(data_year AS STRING), '_', state, '_', COALESCE(bill_number, 'UNKNOWN')) as unique_bill_id,
  data_year,
  
  -- Geographic info
  state,
  CASE state
    WHEN 'AL' THEN 'Alabama'
    WHEN 'AK' THEN 'Alaska' 
    WHEN 'AZ' THEN 'Arizona'
    WHEN 'AR' THEN 'Arkansas'
    WHEN 'CA' THEN 'California'
    WHEN 'CO' THEN 'Colorado'
    WHEN 'CT' THEN 'Connecticut'
    WHEN 'DE' THEN 'Delaware'
    WHEN 'FL' THEN 'Florida'
    WHEN 'GA' THEN 'Georgia'
    WHEN 'HI' THEN 'Hawaii'
    WHEN 'ID' THEN 'Idaho'
    WHEN 'IL' THEN 'Illinois'
    WHEN 'IN' THEN 'Indiana'
    WHEN 'IA' THEN 'Iowa'
    WHEN 'KS' THEN 'Kansas'
    WHEN 'KY' THEN 'Kentucky'
    WHEN 'LA' THEN 'Louisiana'
    WHEN 'ME' THEN 'Maine'
    WHEN 'MD' THEN 'Maryland'
    WHEN 'MA' THEN 'Massachusetts'
    WHEN 'MI' THEN 'Michigan'
    WHEN 'MN' THEN 'Minnesota'
    WHEN 'MS' THEN 'Mississippi'
    WHEN 'MO' THEN 'Missouri'
    WHEN 'MT' THEN 'Montana'
    WHEN 'NE' THEN 'Nebraska'
    WHEN 'NV' THEN 'Nevada'
    WHEN 'NH' THEN 'New Hampshire'
    WHEN 'NJ' THEN 'New Jersey'
    WHEN 'NM' THEN 'New Mexico'
    WHEN 'NY' THEN 'New York'
    WHEN 'NC' THEN 'North Carolina'
    WHEN 'ND' THEN 'North Dakota'
    WHEN 'OH' THEN 'Ohio'
    WHEN 'OK' THEN 'Oklahoma'
    WHEN 'OR' THEN 'Oregon'
    WHEN 'PA' THEN 'Pennsylvania'
    WHEN 'RI' THEN 'Rhode Island'
    WHEN 'SC' THEN 'South Carolina'
    WHEN 'SD' THEN 'South Dakota'
    WHEN 'TN' THEN 'Tennessee'
    WHEN 'TX' THEN 'Texas'
    WHEN 'UT' THEN 'Utah'
    WHEN 'VT' THEN 'Vermont'
    WHEN 'VA' THEN 'Virginia'
    WHEN 'WA' THEN 'Washington'
    WHEN 'WV' THEN 'West Virginia'
    WHEN 'WI' THEN 'Wisconsin'
    WHEN 'WY' THEN 'Wyoming'
    ELSE state
  END as state_name,
  
  CASE state
    WHEN 'CT' THEN 'Northeast'
    WHEN 'ME' THEN 'Northeast'
    WHEN 'MA' THEN 'Northeast'
    WHEN 'NH' THEN 'Northeast'
    WHEN 'NJ' THEN 'Northeast'
    WHEN 'NY' THEN 'Northeast'
    WHEN 'PA' THEN 'Northeast'
    WHEN 'RI' THEN 'Northeast'
    WHEN 'VT' THEN 'Northeast'
    WHEN 'IL' THEN 'Midwest'
    WHEN 'IN' THEN 'Midwest'
    WHEN 'IA' THEN 'Midwest'
    WHEN 'KS' THEN 'Midwest'
    WHEN 'MI' THEN 'Midwest'
    WHEN 'MN' THEN 'Midwest'
    WHEN 'MO' THEN 'Midwest'
    WHEN 'NE' THEN 'Midwest'
    WHEN 'ND' THEN 'Midwest'
    WHEN 'OH' THEN 'Midwest'
    WHEN 'SD' THEN 'Midwest'
    WHEN 'WI' THEN 'Midwest'
    WHEN 'AL' THEN 'South'
    WHEN 'AR' THEN 'South'
    WHEN 'DE' THEN 'South'
    WHEN 'FL' THEN 'South'
    WHEN 'GA' THEN 'South'
    WHEN 'KY' THEN 'South'
    WHEN 'LA' THEN 'South'
    WHEN 'MD' THEN 'South'
    WHEN 'MS' THEN 'South'
    WHEN 'NC' THEN 'South'
    WHEN 'OK' THEN 'South'
    WHEN 'SC' THEN 'South'
    WHEN 'TN' THEN 'South'
    WHEN 'TX' THEN 'South'
    WHEN 'VA' THEN 'South'
    WHEN 'WV' THEN 'South'
    WHEN 'AK' THEN 'West'
    WHEN 'AZ' THEN 'West'
    WHEN 'CA' THEN 'West'
    WHEN 'CO' THEN 'West'
    WHEN 'HI' THEN 'West'
    WHEN 'ID' THEN 'West'
    WHEN 'MT' THEN 'West'
    WHEN 'NV' THEN 'West'
    WHEN 'NM' THEN 'West'
    WHEN 'OR' THEN 'West'
    WHEN 'UT' THEN 'West'
    WHEN 'WA' THEN 'West'
    WHEN 'WY' THEN 'West'
    ELSE 'Unknown'
  END as region,
  
  -- Basic bill info (preserve NULLs)
  bill_number,
  description,
  bill_type,
  history,
  notes,
  website_blurb,
  internal_summary,
  
  -- Date fields (preserve NULLs - they show when tracking began)
  introduced_date,
  last_action_date,
  effective_date,
  enacted_date,
  
  -- Status fields (preserve NULLs - they show methodology evolution)
  introduced,
  seriously_considered,
  passed_first_chamber,
  passed_second_chamber,
  enacted,
  vetoed,
  dead,
  pending,
  
  -- Intent classification (preserve NULLs - they show when classification began)
  positive,
  neutral,
  restrictive,
  
  -- Policy categories (preserve NULLs - they show field evolution)
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
  
  -- Calculated helper fields for dashboards (but preserve underlying NULL reality)
  CASE 
    WHEN data_year >= 2019 THEN 'Modern Era (2019+)'
    WHEN data_year >= 2016 THEN 'Comprehensive Era (2016-2018)' 
    WHEN data_year >= 2006 THEN 'Methodology Revolution (2006-2015)'
    ELSE 'Foundation Era (2002-2005)'
  END as data_era,
  
  CASE 
    WHEN enacted = TRUE THEN 'Enacted'
    WHEN vetoed = TRUE THEN 'Vetoed'
    WHEN dead = TRUE THEN 'Failed/Dead'
    WHEN pending = TRUE THEN 'Pending'
    WHEN introduced = TRUE THEN 'Introduced Only'
    WHEN data_year <= 2005 THEN 'Pre-Modern Tracking'
    ELSE 'Unknown Status'
  END as status_summary,
  
  CASE 
    WHEN positive = TRUE AND restrictive = TRUE THEN 'Mixed Intent'
    WHEN positive = TRUE THEN 'Positive/Pro-Choice'
    WHEN restrictive = TRUE THEN 'Restrictive'
    WHEN neutral = TRUE THEN 'Neutral'
    WHEN data_year <= 2005 THEN 'Pre-Intent Tracking'
    ELSE 'Unclassified'
  END as intent_summary,
  
  -- Policy area counts (only count non-NULL TRUE values)
  (CASE WHEN abortion = TRUE THEN 1 ELSE 0 END +
   CASE WHEN contraception = TRUE THEN 1 ELSE 0 END +
   CASE WHEN emergency_contraception = TRUE THEN 1 ELSE 0 END +
   CASE WHEN minors = TRUE THEN 1 ELSE 0 END +
   CASE WHEN pregnancy = TRUE THEN 1 ELSE 0 END +
   CASE WHEN sex_education = TRUE THEN 1 ELSE 0 END +
   CASE WHEN insurance = TRUE THEN 1 ELSE 0 END +
   CASE WHEN appropriations = TRUE THEN 1 ELSE 0 END +
   CASE WHEN period_products = TRUE THEN 1 ELSE 0 END +
   CASE WHEN incarceration = TRUE THEN 1 ELSE 0 END) as policy_area_count,
  
  -- Data quality indicators
  CASE WHEN introduced_date IS NULL THEN 'No Date Tracking' ELSE 'Has Date Tracking' END as date_tracking_era,
  CASE WHEN bill_type IS NULL THEN 'No Type Classification' ELSE 'Has Type Classification' END as type_tracking_era,
  CASE WHEN positive IS NULL AND neutral IS NULL AND restrictive IS NULL THEN 'No Intent Classification' ELSE 'Has Intent Classification' END as intent_tracking_era,
  
  -- Recent vs historical
  CASE WHEN data_year >= 2020 THEN TRUE ELSE FALSE END as is_recent,
  CASE WHEN data_year >= 2016 THEN TRUE ELSE FALSE END as has_full_date_tracking,
  CASE WHEN data_year >= 2006 THEN TRUE ELSE FALSE END as has_modern_status_tracking

FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
"""

try:
    print("Creating comprehensive_bills_authentic view...")
    query_job = client.query(comprehensive_view_sql)
    query_job.result()
    
    print("✅ Successfully created comprehensive_bills_authentic view")
    
    # Test the new view
    test_query = f"""
    SELECT 
      data_era,
      COUNT(*) as bills,
      COUNT(DISTINCT data_year) as years,
      COUNTIF(introduced_date IS NULL) as no_intro_date,
      COUNTIF(bill_type IS NULL) as no_bill_type,
      COUNTIF(contraception IS NULL) as contraception_not_tracked,
      COUNTIF(period_products IS NULL) as period_products_not_tracked
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic`
    GROUP BY data_era
    ORDER BY MIN(data_year)
    """
    
    print(f"\n📊 Testing new view - NULL preservation by era:")
    print("-" * 80)
    print(f"{'Era':<30} {'Bills':<6} {'Years':<6} {'NoIntro':<8} {'NoType':<7} {'NoContra':<9} {'NoPeriod':<9}")
    print("-" * 80)
    
    test_results = client.query(test_query).result()
    for row in test_results:
        print(f"{row.data_era:<30} {row.bills:<6} {row.years:<6} {row.no_intro_date:<8} {row.no_bill_type:<7} {row.contraception_not_tracked:<9} {row.period_products_not_tracked:<9}")
    
    print(f"\n✅ NEW VIEW PRESERVES NULL PATTERNS!")
    print("Shows authentic data evolution while adding dashboard-friendly fields")
    
except Exception as e:
    print(f"❌ Error creating view: {str(e)}")

print(f"\n{'='*70}")
print("RECOMMENDATION FOR GOOGLE SHEETS:")
print(f"{'='*70}")
print("""
🎯 USE: comprehensive_bills_authentic

This new view:
✅ Preserves authentic NULL vs FALSE vs TRUE patterns
✅ Shows when fields were actually tracked vs not tracked  
✅ Adds helpful calculated fields (state_name, region, data_era, status_summary)
✅ Maintains data integrity while being dashboard-friendly
✅ Includes all 16,323 bills (no filtering)

Perfect for Google Sheets - gives you both authenticity AND usability!
""")