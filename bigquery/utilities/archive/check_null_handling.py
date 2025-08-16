from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

print("🔍 CHECKING NULL HANDLING: comprehensive_bills_authentic vs all_historical_bills_unified")
print("=" * 90)

# Check NULL patterns in both tables for key fields that should have NULLs
comparison_query = """
WITH comprehensive_nulls AS (
  SELECT 
    'comprehensive_bills_authentic' as table_name,
    data_year,
    COUNT(*) as total_bills,
    COUNTIF(introduced_date IS NULL) as null_introduced_date,
    COUNTIF(bill_type IS NULL) as null_bill_type,
    COUNTIF(contraception IS NULL) as null_contraception,
    COUNTIF(period_products IS NULL) as null_period_products,
    COUNTIF(positive IS NULL) as null_positive_intent
  FROM `{os.getenv('GCP_PROJECT_ID')}.legislative_tracker_historical.comprehensive_bills_authentic`
  GROUP BY data_year
),
unified_nulls AS (
  SELECT 
    'all_historical_bills_unified' as table_name,
    data_year,
    COUNT(*) as total_bills,
    COUNTIF(introduced_date IS NULL) as null_introduced_date,
    COUNTIF(bill_type IS NULL) as null_bill_type,
    COUNTIF(contraception IS NULL) as null_contraception,
    COUNTIF(period_products IS NULL) as null_period_products,
    COUNTIF(positive IS NULL) as null_positive_intent
  FROM `{os.getenv('GCP_PROJECT_ID')}.legislative_tracker_historical.all_historical_bills_unified`
  GROUP BY data_year
)
SELECT * FROM comprehensive_nulls
UNION ALL
SELECT * FROM unified_nulls
ORDER BY data_year, table_name
"""

print("📊 Comparing NULL patterns for key fields that SHOULD have NULLs in early years:")
print("-" * 90)
print(f"{'Year':<6} {'Table':<25} {'Bills':<6} {'IntroDate':<10} {'BillType':<9} {'Contracept':<11} {'PeriodProd':<10} {'PosIntent':<9}")
print("-" * 90)

results = client.query(comparison_query).result()
for row in results:
    table_short = row.table_name.replace('_historical_bills', '').replace('comprehensive_bills_authentic', 'comprehensive')
    print(f"{row.data_year:<6} {table_short:<25} {row.total_bills:<6} {row.null_introduced_date:<10} {row.null_bill_type:<9} {row.null_contraception:<11} {row.null_period_products:<10} {row.null_positive_intent:<9}")

print(f"\n{'='*90}")
print("CHECKING SPECIFIC PROBLEM CASES:")
print(f"{'='*90}")

# Check specific cases where we KNOW there should be NULLs
problem_cases = [
    ("Introduced Date 2002", "introduced_date IS NULL", "data_year = 2002"),
    ("Bill Type 2002", "bill_type IS NULL", "data_year = 2002"), 
    ("Contraception 2006", "contraception IS NULL", "data_year = 2006"),
    ("Period Products 2018", "period_products IS NULL", "data_year = 2018"),
    ("Positive Intent 2002", "positive IS NULL", "data_year = 2002")
]

for case_name, null_condition, year_condition in problem_cases:
    print(f"\n🔍 {case_name}:")
    
    for table in ["all_historical_bills_unified", "comprehensive_bills_authentic"]:
        check_query = f"""
        SELECT 
          '{table}' as table_name,
          COUNT(*) as total_bills,
          COUNTIF({null_condition}) as should_be_null,
          COUNTIF({null_condition}) / COUNT(*) * 100 as null_percentage
        FROM `{os.getenv('GCP_PROJECT_ID')}.legislative_tracker_historical.{table}`
        WHERE {year_condition}
        """
        
        result = client.query(check_query).result()
        for row in result:
            table_short = row.table_name.replace('_historical_bills', '').replace('comprehensive_bills_authentic', 'comprehensive')
            print(f"  {table_short:<25}: {row.should_be_null:>3}/{row.total_bills:<3} bills ({row.null_percentage:>5.1f}% NULL)")

print(f"\n{'='*90}")
print("DIAGNOSIS:")
print(f"{'='*90}")

# Check if comprehensive_bills_authentic is filtering out records or converting NULLs
diagnosis_query = f"""
SELECT 
  'Record Count Check' as check_type,
  (SELECT COUNT(*) FROM `{os.getenv('GCP_PROJECT_ID')}.legislative_tracker_historical.all_historical_bills_unified`) as unified_count,
  (SELECT COUNT(*) FROM `{os.getenv('GCP_PROJECT_ID')}.legislative_tracker_historical.comprehensive_bills_authentic`) as comprehensive_count
"""

result = client.query(diagnosis_query).result()
for row in result:
    if row.unified_count != row.comprehensive_count:
        print(f"❌ RECORD COUNT MISMATCH:")
        print(f"   all_historical_bills_unified: {row.unified_count:,} bills")
        print(f"   comprehensive_bills_authentic: {row.comprehensive_count:,} bills")
        print(f"   Missing: {row.unified_count - row.comprehensive_count:,} bills")
    else:
        print(f"✅ RECORD COUNT MATCH: Both tables have {row.unified_count:,} bills")

print(f"\n💡 RECOMMENDATION:")
print("-" * 50)
print("""
If comprehensive_bills_authentic is converting NULLs to FALSE or filtering records:

🎯 USE: all_historical_bills_unified for Google Sheets
   - Preserves authentic NULL vs FALSE distinction  
   - Shows true data evolution patterns
   - Authentic representation of what was tracked when

⚠️  AVOID: comprehensive_bills_authentic if it's masking data reality
   - May be designed for dashboards that need clean data
   - Could be converting NULLs to FALSE for visualization
   - Obscures the methodology evolution story
""")