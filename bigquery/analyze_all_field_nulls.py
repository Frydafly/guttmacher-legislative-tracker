from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

# Query to analyze ALL field types - NULL vs populated by year
query = """
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Basic identifier fields
  COUNTIF(state IS NOT NULL) / COUNT(*) * 100 as state_populated_pct,
  COUNTIF(state IS NULL) / COUNT(*) * 100 as state_null_pct,
  
  COUNTIF(bill_number IS NOT NULL) / COUNT(*) * 100 as bill_number_populated_pct,
  COUNTIF(bill_number IS NULL) / COUNT(*) * 100 as bill_number_null_pct,
  
  COUNTIF(bill_type IS NOT NULL) / COUNT(*) * 100 as bill_type_populated_pct,
  COUNTIF(bill_type IS NULL) / COUNT(*) * 100 as bill_type_null_pct,
  
  -- Text description fields
  COUNTIF(description IS NOT NULL) / COUNT(*) * 100 as description_populated_pct,
  COUNTIF(description IS NULL) / COUNT(*) * 100 as description_null_pct,
  
  COUNTIF(internal_summary IS NOT NULL) / COUNT(*) * 100 as internal_summary_populated_pct,
  COUNTIF(internal_summary IS NULL) / COUNT(*) * 100 as internal_summary_null_pct,
  
  COUNTIF(notes IS NOT NULL) / COUNT(*) * 100 as notes_populated_pct,
  COUNTIF(notes IS NULL) / COUNT(*) * 100 as notes_null_pct,
  
  COUNTIF(history IS NOT NULL) / COUNT(*) * 100 as history_populated_pct,
  COUNTIF(history IS NULL) / COUNT(*) * 100 as history_null_pct,
  
  COUNTIF(website_blurb IS NOT NULL) / COUNT(*) * 100 as website_blurb_populated_pct,
  COUNTIF(website_blurb IS NULL) / COUNT(*) * 100 as website_blurb_null_pct,
  
  -- Date fields
  COUNTIF(introduced_date IS NOT NULL) / COUNT(*) * 100 as introduced_date_populated_pct,
  COUNTIF(introduced_date IS NULL) / COUNT(*) * 100 as introduced_date_null_pct,
  
  COUNTIF(last_action_date IS NOT NULL) / COUNT(*) * 100 as last_action_date_populated_pct,
  COUNTIF(last_action_date IS NULL) / COUNT(*) * 100 as last_action_date_null_pct,
  
  COUNTIF(effective_date IS NOT NULL) / COUNT(*) * 100 as effective_date_populated_pct,
  COUNTIF(effective_date IS NULL) / COUNT(*) * 100 as effective_date_null_pct,
  
  COUNTIF(enacted_date IS NOT NULL) / COUNT(*) * 100 as enacted_date_populated_pct,
  COUNTIF(enacted_date IS NULL) / COUNT(*) * 100 as enacted_date_null_pct,
  
  COUNTIF(vetoed_date IS NOT NULL) / COUNT(*) * 100 as vetoed_date_populated_pct,
  COUNTIF(vetoed_date IS NULL) / COUNT(*) * 100 as vetoed_date_null_pct,
  
  COUNTIF(date_last_updated IS NOT NULL) / COUNT(*) * 100 as date_last_updated_populated_pct,
  COUNTIF(date_last_updated IS NULL) / COUNT(*) * 100 as date_last_updated_null_pct,
  
  -- Status fields (should be 100% populated with TRUE/FALSE)
  COUNTIF(introduced IS NOT NULL) / COUNT(*) * 100 as introduced_populated_pct,
  COUNTIF(introduced IS NULL) / COUNT(*) * 100 as introduced_null_pct,
  
  COUNTIF(enacted IS NOT NULL) / COUNT(*) * 100 as enacted_populated_pct,
  COUNTIF(enacted IS NULL) / COUNT(*) * 100 as enacted_null_pct,
  
  COUNTIF(vetoed IS NOT NULL) / COUNT(*) * 100 as vetoed_populated_pct,
  COUNTIF(vetoed IS NULL) / COUNT(*) * 100 as vetoed_null_pct,
  
  COUNTIF(dead IS NOT NULL) / COUNT(*) * 100 as dead_populated_pct,
  COUNTIF(dead IS NULL) / COUNT(*) * 100 as dead_null_pct,
  
  COUNTIF(pending IS NOT NULL) / COUNT(*) * 100 as pending_populated_pct,
  COUNTIF(pending IS NULL) / COUNT(*) * 100 as pending_null_pct,
  
  -- Policy category fields (should be 100% populated with TRUE/FALSE/NULL as data)
  COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100 as abortion_populated_pct,
  COUNTIF(abortion IS NULL) / COUNT(*) * 100 as abortion_null_pct,
  
  COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100 as contraception_populated_pct,
  COUNTIF(contraception IS NULL) / COUNT(*) * 100 as contraception_null_pct,
  
  COUNTIF(minors IS NOT NULL) / COUNT(*) * 100 as minors_populated_pct,
  COUNTIF(minors IS NULL) / COUNT(*) * 100 as minors_null_pct,
  
  COUNTIF(sex_education IS NOT NULL) / COUNT(*) * 100 as sex_education_populated_pct,
  COUNTIF(sex_education IS NULL) / COUNT(*) * 100 as sex_education_null_pct,
  
  COUNTIF(insurance IS NOT NULL) / COUNT(*) * 100 as insurance_populated_pct,
  COUNTIF(insurance IS NULL) / COUNT(*) * 100 as insurance_null_pct,
  
  COUNTIF(pregnancy IS NOT NULL) / COUNT(*) * 100 as pregnancy_populated_pct,
  COUNTIF(pregnancy IS NULL) / COUNT(*) * 100 as pregnancy_null_pct,
  
  -- Intent fields
  COUNTIF(positive IS NOT NULL) / COUNT(*) * 100 as positive_populated_pct,
  COUNTIF(positive IS NULL) / COUNT(*) * 100 as positive_null_pct,
  
  COUNTIF(neutral IS NOT NULL) / COUNT(*) * 100 as neutral_populated_pct,
  COUNTIF(neutral IS NULL) / COUNT(*) * 100 as neutral_null_pct,
  
  COUNTIF(restrictive IS NOT NULL) / COUNT(*) * 100 as restrictive_populated_pct,
  COUNTIF(restrictive IS NULL) / COUNT(*) * 100 as restrictive_null_pct,
  
  -- Topic fields (these might be more sparse)
  COUNTIF(topic_1 IS NOT NULL) / COUNT(*) * 100 as topic_1_populated_pct,
  COUNTIF(topic_1 IS NULL) / COUNT(*) * 100 as topic_1_null_pct,
  
  COUNTIF(topic_2 IS NOT NULL) / COUNT(*) * 100 as topic_2_populated_pct,
  COUNTIF(topic_2 IS NULL) / COUNT(*) * 100 as topic_2_null_pct,
  
  COUNTIF(topic_3 IS NOT NULL) / COUNT(*) * 100 as topic_3_populated_pct,
  COUNTIF(topic_3 IS NULL) / COUNT(*) * 100 as topic_3_null_pct,
  
  -- Bill type categorization fields
  COUNTIF(legislation IS NOT NULL) / COUNT(*) * 100 as legislation_populated_pct,
  COUNTIF(legislation IS NULL) / COUNT(*) * 100 as legislation_null_pct,
  
  COUNTIF(resolution IS NOT NULL) / COUNT(*) * 100 as resolution_populated_pct,
  COUNTIF(resolution IS NULL) / COUNT(*) * 100 as resolution_null_pct,
  
  COUNTIF(constitutional_amendment IS NOT NULL) / COUNT(*) * 100 as constitutional_amendment_populated_pct,
  COUNTIF(constitutional_amendment IS NULL) / COUNT(*) * 100 as constitutional_amendment_null_pct,
  
  COUNTIF(ballot_initiative IS NOT NULL) / COUNT(*) * 100 as ballot_initiative_populated_pct,
  COUNTIF(ballot_initiative IS NULL) / COUNT(*) * 100 as ballot_initiative_null_pct,
  
  COUNTIF(court_case IS NOT NULL) / COUNT(*) * 100 as court_case_populated_pct,
  COUNTIF(court_case IS NULL) / COUNT(*) * 100 as court_case_null_pct,
  
  -- Time period classification fields (these are unusual - likely year ranges)
  COUNTIF(`2005` IS NOT NULL) / COUNT(*) * 100 as period_2005_populated_pct,
  COUNTIF(`2005` IS NULL) / COUNT(*) * 100 as period_2005_null_pct,
  
  COUNTIF(`2006_2007` IS NOT NULL) / COUNT(*) * 100 as period_2006_2007_populated_pct,
  COUNTIF(`2006_2007` IS NULL) / COUNT(*) * 100 as period_2006_2007_null_pct,
  
  COUNTIF(`2008_2014` IS NOT NULL) / COUNT(*) * 100 as period_2008_2014_populated_pct,
  COUNTIF(`2008_2014` IS NULL) / COUNT(*) * 100 as period_2008_2014_null_pct

FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY data_year
ORDER BY data_year
""".replace("{project}", os.getenv('GCP_PROJECT_ID'))

print("Analyzing NULL vs POPULATED rates for ALL field types across all years...")
print("=" * 90)

# Run the query
results = client.query(query).to_dataframe()

def analyze_field_nulls(df, field_categories):
    for category_name, fields in field_categories.items():
        print(f"\n{'='*90}")
        print(f"{category_name.upper()}")
        print(f"{'='*90}")
        
        for field_name, field_description in fields:
            print(f"\n📊 {field_name.upper()}: {field_description}")
            print("-" * 80)
            print(f"{'Year':<6} {'Bills':<6} {'Populated %':<12} {'NULL %':<10} {'Data Quality'}")
            print("-" * 80)
            
            for _, row in df.iterrows():
                year = int(row['data_year'])
                total = row['total_bills']
                populated_pct = row[f'{field_name}_populated_pct']
                null_pct = row[f'{field_name}_null_pct']
                
                # Determine data quality based on population rate
                if populated_pct >= 95:
                    quality = "✅ Excellent"
                elif populated_pct >= 80:
                    quality = "⚠️ Good"
                elif populated_pct >= 50:
                    quality = "🔶 Moderate"
                elif populated_pct >= 20:
                    quality = "❌ Poor"
                else:
                    quality = "💀 Very Poor"
                    
                print(f"{year:<6} {total:<6} {populated_pct:<11.1f}% {null_pct:<9.1f}% {quality}")

# Define field categories
field_categories = {
    "Basic Identifier Fields": [
        ('state', 'State abbreviation'),
        ('bill_number', 'Bill number/identifier'),
        ('bill_type', 'Type of legislation (bill, resolution, etc.)')
    ],
    
    "Text Description Fields": [
        ('description', 'Bill description/title'),
        ('internal_summary', 'Internal summary of bill content'),
        ('notes', 'Additional notes'),
        ('history', 'Legislative history'),
        ('website_blurb', 'Website description')
    ],
    
    "Date Fields": [
        ('introduced_date', 'Date bill was introduced'),
        ('last_action_date', 'Date of most recent action'),
        ('effective_date', 'Date bill takes effect'),
        ('enacted_date', 'Date bill was enacted'),
        ('vetoed_date', 'Date bill was vetoed'),
        ('date_last_updated', 'Date record was last updated')
    ],
    
    "Status Fields (should be 100% populated)": [
        ('introduced', 'Bill was introduced'),
        ('enacted', 'Bill was enacted'),
        ('vetoed', 'Bill was vetoed'),
        ('dead', 'Bill failed/died'),
        ('pending', 'Bill is pending')
    ],
    
    "Core Policy Categories (should be 100% populated)": [
        ('abortion', 'Abortion-related'),
        ('contraception', 'Contraception-related'),
        ('minors', 'Affects minors'),
        ('sex_education', 'Sex education'),
        ('insurance', 'Insurance coverage'),
        ('pregnancy', 'Pregnancy-related')
    ],
    
    "Intent Classification (should be 100% populated)": [
        ('positive', 'Pro-reproductive rights'),
        ('neutral', 'Neutral impact'),
        ('restrictive', 'Restricts reproductive rights')
    ],
    
    "Topic Classification Fields": [
        ('topic_1', 'Primary topic classification'),
        ('topic_2', 'Secondary topic classification'),
        ('topic_3', 'Tertiary topic classification')
    ],
    
    "Bill Type Categories": [
        ('legislation', 'Regular legislation'),
        ('resolution', 'Resolution'),
        ('constitutional_amendment', 'Constitutional amendment'),
        ('ballot_initiative', 'Ballot initiative'),
        ('court_case', 'Court case')
    ],
    
    "Time Period Classification (unusual fields)": [
        ('period_2005', '2005 period classification'),
        ('period_2006_2007', '2006-2007 period classification'),
        ('period_2008_2014', '2008-2014 period classification')
    ]
}

analyze_field_nulls(results, field_categories)

# Summary analysis
print(f"\n{'='*90}")
print("SUMMARY ANALYSIS")
print(f"{'='*90}")

print("\nFields with Perfect Population (100% across all years):")
perfect_fields = []
for category_name, fields in field_categories.items():
    for field_name, field_description in fields:
        if results[f'{field_name}_null_pct'].max() == 0:
            perfect_fields.append((field_name, field_description, category_name))

for field_name, desc, category in perfect_fields:
    print(f"  ✅ {field_name} ({category}): {desc}")

print("\nFields with Major NULL Issues (>50% NULL in any year):")
problem_fields = []
for category_name, fields in field_categories.items():
    for field_name, field_description in fields:
        max_null = results[f'{field_name}_null_pct'].max()
        if max_null > 50:
            problem_fields.append((field_name, field_description, category_name, max_null))

for field_name, desc, category, max_null in sorted(problem_fields, key=lambda x: x[3], reverse=True):
    print(f"  ❌ {field_name} ({category}): {desc} - Max NULL: {max_null:.1f}%")

print("\nFields with Improving Population Over Time:")
improving_fields = []
for category_name, fields in field_categories.items():
    for field_name, field_description in fields:
        early_null = results[results['data_year'] <= 2010][f'{field_name}_null_pct'].mean()
        recent_null = results[results['data_year'] >= 2018][f'{field_name}_null_pct'].mean()
        improvement = early_null - recent_null
        
        if improvement > 10:  # More than 10% improvement
            improving_fields.append((field_name, field_description, early_null, recent_null, improvement))

for field_name, desc, early_null, recent_null, improvement in sorted(improving_fields, key=lambda x: x[4], reverse=True):
    print(f"  📈 {field_name}: {early_null:.1f}% → {recent_null:.1f}% NULL (improved {improvement:.1f}%)")

# Export detailed results
results.to_csv('complete_field_null_analysis.csv', index=False)
print(f"\n💾 Complete field analysis saved to: complete_field_null_analysis.csv")
print(f"Total years analyzed: {len(results)}")
print(f"Total bills across all years: {results['total_bills'].sum():,}")
print(f"Total fields analyzed: {sum(len(fields) for fields in field_categories.values())}")