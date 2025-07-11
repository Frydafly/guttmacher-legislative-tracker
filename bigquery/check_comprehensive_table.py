from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

print("📊 CHECKING COMPREHENSIVE BILLS TABLE FOR CSV EXPORT")
print("=" * 70)

# Check what's actually in the comprehensive table
query = """
SELECT *
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_comprehensive_bills`
LIMIT 5
"""

print("🔍 Sample data from looker_comprehensive_bills:")
try:
    results = client.query(query).result()
    
    # Get column names from first row
    first_row = next(iter(results), None)
    if first_row:
        columns = list(first_row.keys())
        print(f"\n📋 Available columns ({len(columns)} total):")
        for i, col in enumerate(columns, 1):
            print(f"{i:2d}. {col}")
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM `guttmacher-legislative-tracker.legislative_tracker_historical.looker_comprehensive_bills`"
        count_result = client.query(count_query).result()
        for row in count_result:
            print(f"\n📊 Total rows: {row.total:,}")
    
except Exception as e:
    print(f"❌ Error accessing looker_comprehensive_bills: {e}")
    print("\n🔄 Checking all_historical_bills_unified instead...")
    
    # Fallback to unified view
    query2 = """
    SELECT *
    FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
    LIMIT 3
    """
    
    try:
        results2 = client.query(query2).result()
        first_row2 = next(iter(results2), None)
        if first_row2:
            columns2 = list(first_row2.keys())
            print(f"\n📋 all_historical_bills_unified columns ({len(columns2)} total):")
            for i, col in enumerate(columns2, 1):
                print(f"{i:2d}. {col}")
            
            # Get total count
            count_query2 = "SELECT COUNT(*) as total FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`"
            count_result2 = client.query(count_query2).result()
            for row in count_result2:
                print(f"\n📊 Total rows: {row.total:,}")
    except Exception as e2:
        print(f"❌ Error accessing all_historical_bills_unified: {e2}")

print(f"\n{'='*70}")
print("RECOMMENDATION FOR GOOGLE SHEETS EXPORT:")
print(f"{'='*70}")

print("""
For your team's Google Sheets comprehensive view, I recommend:

🎯 PRIMARY OPTION: `looker_comprehensive_bills`
   - Pre-built for analysis and dashboards
   - Includes calculated fields and clean structure
   - Optimized for non-technical users

🔄 FALLBACK OPTION: `all_historical_bills_unified` 
   - Raw unified data from all years
   - Complete field set but may need filtering
   - More technical but comprehensive

⚠️  GOOGLE SHEETS LIMITS:
   - Maximum 10 million cells (roughly 16k rows × 600+ columns)
   - With 16,323 bills, you may need to export by year ranges
   - Consider filtering to essential columns only

💡 EXPORT STRATEGY:
   1. Export core fields only (state, year, bill_number, description, policy categories, status, intent)
   2. Create separate sheets for different analysis needs
   3. Use raw_data_tracking_by_year for field evolution summary
""")

# Show a sample export query
print(f"\n📝 SAMPLE EXPORT QUERY FOR GOOGLE SHEETS:")
print("-" * 50)
print("""
SELECT 
  data_year,
  bill_number,
  state,
  description,
  bill_type,
  introduced_date,
  last_action_date,
  introduced,
  enacted,
  vetoed,
  dead,
  pending,
  abortion,
  contraception,
  minors,
  sex_education,
  insurance,
  pregnancy,
  positive,
  neutral,
  restrictive
FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`
WHERE data_year >= 2020  -- Recent years for manageable size
ORDER BY data_year DESC, state, bill_number
""")