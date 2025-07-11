from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

print("Analyzing RAW data availability by year - what was actually in each original database")
print("=" * 90)

# Query to understand what fields actually had data (not NULL) in each year
# This tells us what the original researchers were tracking each year
query = """
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Basic fields - these should be in every year
  SUM(CASE WHEN state IS NOT NULL THEN 1 ELSE 0 END) as has_state,
  SUM(CASE WHEN bill_number IS NOT NULL THEN 1 ELSE 0 END) as has_bill_number,
  SUM(CASE WHEN description IS NOT NULL THEN 1 ELSE 0 END) as has_description,
  SUM(CASE WHEN bill_type IS NOT NULL THEN 1 ELSE 0 END) as has_bill_type,
  
  -- Date fields - when did they start tracking these?
  SUM(CASE WHEN introduced_date IS NOT NULL THEN 1 ELSE 0 END) as has_introduced_date,
  SUM(CASE WHEN last_action_date IS NOT NULL THEN 1 ELSE 0 END) as has_last_action_date,
  SUM(CASE WHEN effective_date IS NOT NULL THEN 1 ELSE 0 END) as has_effective_date,
  SUM(CASE WHEN enacted_date IS NOT NULL THEN 1 ELSE 0 END) as has_enacted_date,
  
  -- Text fields - when did they start collecting these?
  SUM(CASE WHEN internal_summary IS NOT NULL THEN 1 ELSE 0 END) as has_internal_summary,
  SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) as has_notes,
  SUM(CASE WHEN history IS NOT NULL THEN 1 ELSE 0 END) as has_history,
  SUM(CASE WHEN website_blurb IS NOT NULL THEN 1 ELSE 0 END) as has_website_blurb,
  
  -- Status tracking - when did they start tracking legislative outcomes?
  SUM(CASE WHEN introduced = TRUE THEN 1 ELSE 0 END) as bills_marked_introduced,
  SUM(CASE WHEN enacted = TRUE THEN 1 ELSE 0 END) as bills_marked_enacted,
  SUM(CASE WHEN vetoed = TRUE THEN 1 ELSE 0 END) as bills_marked_vetoed,
  SUM(CASE WHEN dead = TRUE THEN 1 ELSE 0 END) as bills_marked_dead,
  SUM(CASE WHEN pending = TRUE THEN 1 ELSE 0 END) as bills_marked_pending,
  
  -- Policy categories - what were they tracking?
  SUM(CASE WHEN abortion = TRUE THEN 1 ELSE 0 END) as bills_marked_abortion,
  SUM(CASE WHEN contraception = TRUE THEN 1 ELSE 0 END) as bills_marked_contraception,
  SUM(CASE WHEN minors = TRUE THEN 1 ELSE 0 END) as bills_marked_minors,
  SUM(CASE WHEN sex_education = TRUE THEN 1 ELSE 0 END) as bills_marked_sex_education,
  SUM(CASE WHEN insurance = TRUE THEN 1 ELSE 0 END) as bills_marked_insurance,
  SUM(CASE WHEN pregnancy = TRUE THEN 1 ELSE 0 END) as bills_marked_pregnancy,
  SUM(CASE WHEN emergency_contraception = TRUE THEN 1 ELSE 0 END) as bills_marked_emergency_contraception,
  SUM(CASE WHEN appropriations = TRUE THEN 1 ELSE 0 END) as bills_marked_appropriations,
  
  -- Intent classification - when did this start?
  SUM(CASE WHEN positive = TRUE THEN 1 ELSE 0 END) as bills_marked_positive,
  SUM(CASE WHEN neutral = TRUE THEN 1 ELSE 0 END) as bills_marked_neutral,
  SUM(CASE WHEN restrictive = TRUE THEN 1 ELSE 0 END) as bills_marked_restrictive,
  
  -- Newer categories
  SUM(CASE WHEN period_products = TRUE THEN 1 ELSE 0 END) as bills_marked_period_products,
  SUM(CASE WHEN incarceration = TRUE THEN 1 ELSE 0 END) as bills_marked_incarceration

FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY data_year
ORDER BY data_year
""".replace("{project}", os.getenv('GCP_PROJECT_ID'))

results = client.query(query).to_dataframe()

def analyze_field_availability(df, field_categories):
    for category_name, fields in field_categories.items():
        print(f"\n{'='*90}")
        print(f"{category_name.upper()}")
        print(f"{'='*90}")
        
        for field_base, field_description in fields:
            field_name = f"has_{field_base}" if field_base in ['state', 'bill_number', 'description', 'bill_type', 'introduced_date', 'last_action_date', 'effective_date', 'enacted_date', 'internal_summary', 'notes', 'history', 'website_blurb'] else f"bills_marked_{field_base}"
            
            print(f"\n📊 {field_base.upper()}: {field_description}")
            print("-" * 80)
            print(f"{'Year':<6} {'Total':<6} {'Available':<10} {'%Available':<12} {'Data Status'}")
            print("-" * 80)
            
            for _, row in df.iterrows():
                year = int(row['data_year'])
                total = row['total_bills']
                available = row[field_name] if field_name in row else 0
                pct_available = (available / total * 100) if total > 0 else 0
                
                # Determine what this means for data availability
                if field_base in ['state', 'bill_number', 'description']:
                    # Basic fields should always be available
                    if pct_available >= 95:
                        status = "✅ Complete"
                    elif pct_available >= 80:
                        status = "⚠️ Mostly Complete"
                    else:
                        status = "❌ Incomplete"
                elif field_base in ['introduced_date', 'last_action_date', 'effective_date', 'enacted_date', 'internal_summary', 'website_blurb']:
                    # Date/text fields - availability shows when tracking started
                    if pct_available >= 50:
                        status = "✅ Tracked This Year"
                    elif pct_available >= 10:
                        status = "⚠️ Partially Tracked"
                    elif pct_available > 0:
                        status = "🔍 Limited Tracking"
                    else:
                        status = "❌ Not Tracked"
                else:
                    # Policy/status fields - shows actual activity
                    if pct_available >= 30:
                        status = "🔥 High Activity"
                    elif pct_available >= 10:
                        status = "📊 Moderate Activity"
                    elif pct_available >= 1:
                        status = "📍 Some Activity"
                    else:
                        status = "⚪ No Activity"
                
                print(f"{year:<6} {total:<6} {available:<10} {pct_available:<11.1f}% {status}")

# Define field categories focused on data availability
field_categories = {
    "Basic Data Collection": [
        ('state', 'State identifier'),
        ('bill_number', 'Bill number/ID'),
        ('description', 'Bill description'),
        ('bill_type', 'Type of legislation'),
        ('history', 'Legislative history text')
    ],
    
    "Date Tracking Evolution": [
        ('introduced_date', 'When they started tracking introduction dates'),
        ('last_action_date', 'When they started tracking action dates'),
        ('effective_date', 'When they started tracking effective dates'),
        ('enacted_date', 'When they started tracking enactment dates')
    ],
    
    "Text Data Collection": [
        ('internal_summary', 'Internal bill summaries'),
        ('notes', 'Additional notes'),
        ('website_blurb', 'Website descriptions')
    ],
    
    "Legislative Status Tracking": [
        ('introduced', 'Bills marked as introduced'),
        ('enacted', 'Bills marked as enacted'),
        ('vetoed', 'Bills marked as vetoed'),
        ('dead', 'Bills marked as dead/failed'),
        ('pending', 'Bills marked as pending')
    ],
    
    "Policy Category Tracking": [
        ('abortion', 'Abortion-related bills identified'),
        ('contraception', 'Contraception-related bills identified'),
        ('minors', 'Minor-related bills identified'),
        ('sex_education', 'Sex education bills identified'),
        ('insurance', 'Insurance-related bills identified'),
        ('pregnancy', 'Pregnancy-related bills identified'),
        ('emergency_contraception', 'Emergency contraception bills identified'),
        ('appropriations', 'Appropriations bills identified')
    ],
    
    "Intent Classification Evolution": [
        ('positive', 'Bills classified as positive/pro-choice'),
        ('neutral', 'Bills classified as neutral'),
        ('restrictive', 'Bills classified as restrictive')
    ],
    
    "Emerging Policy Areas": [
        ('period_products', 'Period products bills identified'),
        ('incarceration', 'Incarceration-related bills identified')
    ]
}

analyze_field_availability(results, field_categories)

# Summary insights
print(f"\n{'='*90}")
print("SUMMARY: WHAT WAS ACTUALLY COLLECTED EACH YEAR")
print(f"{'='*90}")

print("\n🔍 DATA COLLECTION EVOLUTION:")

print("\n**2002-2005 (Foundation Era):**")
for year in [2002, 2003, 2004, 2005]:
    if year in results['data_year'].values:
        year_data = results[results['data_year'] == year].iloc[0]
        print(f"  {year}: {int(year_data['total_bills'])} bills")
        print(f"    - Basic data: {year_data['has_state']}/{year_data['total_bills']} state, {year_data['has_description']}/{year_data['total_bills']} descriptions")
        print(f"    - Policy focus: {year_data['bills_marked_abortion']} abortion, {year_data['bills_marked_contraception']} contraception")
        print(f"    - Date tracking: {year_data['has_introduced_date']} introduced dates, {year_data['has_last_action_date']} action dates")

print("\n**2006-2015 (Expansion Era):**")
print("  Key changes: Bill type tracking began, legislative status methodology evolved")

print("\n**2016+ (Modern Era):**")
print("  Key changes: Systematic date tracking, internal summaries (2019+)")

print("\n🎯 KEY INSIGHTS FOR TEAM:")
print("- **What changed when**: Clear evolution in what researchers tracked each year")
print("- **Data availability vs data meaning**: NULLs show what wasn't tracked yet, not missing data")
print("- **Original research focus**: Early years focused on basic identification, later years added process tracking")

# Export results
results.to_csv('raw_data_availability_by_year.csv', index=False)
print(f"\n💾 Raw data availability analysis saved to: raw_data_availability_by_year.csv")
print(f"This shows exactly what was collected in each original database file.")