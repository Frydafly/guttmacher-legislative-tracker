from google.cloud import bigquery
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

# Query to analyze TRUE/FALSE/NULL progression by year for all fields
query = """
SELECT 
  data_year,
  COUNT(*) as total_bills,
  
  -- Status fields - TRUE/FALSE/NULL breakdown
  COUNTIF(introduced = TRUE) as introduced_true,
  COUNTIF(introduced = FALSE) as introduced_false,
  COUNTIF(introduced IS NULL) as introduced_null,
  
  COUNTIF(enacted = TRUE) as enacted_true,
  COUNTIF(enacted = FALSE) as enacted_false,
  COUNTIF(enacted IS NULL) as enacted_null,
  
  COUNTIF(vetoed = TRUE) as vetoed_true,
  COUNTIF(vetoed = FALSE) as vetoed_false,
  COUNTIF(vetoed IS NULL) as vetoed_null,
  
  COUNTIF(dead = TRUE) as dead_true,
  COUNTIF(dead = FALSE) as dead_false,
  COUNTIF(dead IS NULL) as dead_null,
  
  COUNTIF(pending = TRUE) as pending_true,
  COUNTIF(pending = FALSE) as pending_false,
  COUNTIF(pending IS NULL) as pending_null,
  
  COUNTIF(passed_first_chamber = TRUE) as passed_first_chamber_true,
  COUNTIF(passed_first_chamber = FALSE) as passed_first_chamber_false,
  COUNTIF(passed_first_chamber IS NULL) as passed_first_chamber_null,
  
  COUNTIF(passed_second_chamber = TRUE) as passed_second_chamber_true,
  COUNTIF(passed_second_chamber = FALSE) as passed_second_chamber_false,
  COUNTIF(passed_second_chamber IS NULL) as passed_second_chamber_null,
  
  COUNTIF(seriously_considered = TRUE) as seriously_considered_true,
  COUNTIF(seriously_considered = FALSE) as seriously_considered_false,
  COUNTIF(seriously_considered IS NULL) as seriously_considered_null,
  
  -- Policy categories - TRUE/FALSE/NULL breakdown
  COUNTIF(abortion = TRUE) as abortion_true,
  COUNTIF(abortion = FALSE) as abortion_false,
  COUNTIF(abortion IS NULL) as abortion_null,
  
  COUNTIF(contraception = TRUE) as contraception_true,
  COUNTIF(contraception = FALSE) as contraception_false,
  COUNTIF(contraception IS NULL) as contraception_null,
  
  COUNTIF(minors = TRUE) as minors_true,
  COUNTIF(minors = FALSE) as minors_false,
  COUNTIF(minors IS NULL) as minors_null,
  
  COUNTIF(sex_education = TRUE) as sex_education_true,
  COUNTIF(sex_education = FALSE) as sex_education_false,
  COUNTIF(sex_education IS NULL) as sex_education_null,
  
  COUNTIF(insurance = TRUE) as insurance_true,
  COUNTIF(insurance = FALSE) as insurance_false,
  COUNTIF(insurance IS NULL) as insurance_null,
  
  COUNTIF(pregnancy = TRUE) as pregnancy_true,
  COUNTIF(pregnancy = FALSE) as pregnancy_false,
  COUNTIF(pregnancy IS NULL) as pregnancy_null,
  
  COUNTIF(emergency_contraception = TRUE) as emergency_contraception_true,
  COUNTIF(emergency_contraception = FALSE) as emergency_contraception_false,
  COUNTIF(emergency_contraception IS NULL) as emergency_contraception_null,
  
  COUNTIF(appropriations = TRUE) as appropriations_true,
  COUNTIF(appropriations = FALSE) as appropriations_false,
  COUNTIF(appropriations IS NULL) as appropriations_null,
  
  -- Intent fields - TRUE/FALSE/NULL breakdown
  COUNTIF(positive = TRUE) as positive_true,
  COUNTIF(positive = FALSE) as positive_false,
  COUNTIF(positive IS NULL) as positive_null,
  
  COUNTIF(neutral = TRUE) as neutral_true,
  COUNTIF(neutral = FALSE) as neutral_false,
  COUNTIF(neutral IS NULL) as neutral_null,
  
  COUNTIF(restrictive = TRUE) as restrictive_true,
  COUNTIF(restrictive = FALSE) as restrictive_false,
  COUNTIF(restrictive IS NULL) as restrictive_null,
  
  -- Newer fields
  COUNTIF(period_products = TRUE) as period_products_true,
  COUNTIF(period_products = FALSE) as period_products_false,
  COUNTIF(period_products IS NULL) as period_products_null,
  
  COUNTIF(incarceration = TRUE) as incarceration_true,
  COUNTIF(incarceration = FALSE) as incarceration_false,
  COUNTIF(incarceration IS NULL) as incarceration_null

FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY data_year
ORDER BY data_year
""".replace("{project}", os.getenv('GCP_PROJECT_ID'))

print("Analyzing year-by-year TRUE/FALSE/NULL progression for all fields...")
print("=" * 80)

# Run the query
results = client.query(query).to_dataframe()

def format_percentage(value, total):
    if total == 0:
        return "0.0%"
    return f"{(value/total)*100:.1f}%"

def analyze_field_progression(df, field_name, field_description):
    print(f"\n📊 {field_name.upper()}: {field_description}")
    print("-" * 60)
    
    print(f"{'Year':<6} {'Bills':<6} {'TRUE':<12} {'FALSE':<12} {'NULL':<12} {'Data Quality'}")
    print("-" * 60)
    
    for _, row in df.iterrows():
        year = int(row['data_year'])
        total = row['total_bills']
        true_count = row[f'{field_name}_true']
        false_count = row[f'{field_name}_false']
        null_count = row[f'{field_name}_null']
        
        true_pct = format_percentage(true_count, total)
        false_pct = format_percentage(false_count, total)
        null_pct = format_percentage(null_count, total)
        
        # Determine data quality
        if null_count == 0:
            quality = "✅ Complete"
        elif null_count < total * 0.1:
            quality = "⚠️ Mostly Complete"
        else:
            quality = "❌ Sparse"
            
        print(f"{year:<6} {total:<6} {true_pct:<12} {false_pct:<12} {null_pct:<12} {quality}")

# Status fields analysis
status_fields = [
    ('introduced', 'Bill was introduced in legislature'),
    ('enacted', 'Bill became law'),
    ('vetoed', 'Bill was vetoed'), 
    ('dead', 'Bill failed/died'),
    ('pending', 'Bill is still active'),
    ('passed_first_chamber', 'Passed first chamber'),
    ('passed_second_chamber', 'Passed second chamber'),
    ('seriously_considered', 'Received serious consideration')
]

print("\n" + "="*80)
print("STATUS FIELDS PROGRESSION")
print("="*80)

for field, desc in status_fields:
    analyze_field_progression(results, field, desc)

# Policy category fields
policy_fields = [
    ('abortion', 'Abortion-related bills'),
    ('contraception', 'Contraception/birth control bills'),
    ('minors', 'Bills affecting minors/teens'),
    ('sex_education', 'Sex education bills'),
    ('insurance', 'Insurance coverage bills'),
    ('pregnancy', 'Pregnancy-related bills'),
    ('emergency_contraception', 'Emergency contraception bills'),
    ('appropriations', 'Funding/appropriations bills')
]

print("\n" + "="*80)
print("POLICY CATEGORY PROGRESSION")
print("="*80)

for field, desc in policy_fields:
    analyze_field_progression(results, field, desc)

# Intent fields
intent_fields = [
    ('positive', 'Pro-reproductive rights bills'),
    ('neutral', 'Neutral impact bills'),
    ('restrictive', 'Bills restricting reproductive rights')
]

print("\n" + "="*80)
print("INTENT CLASSIFICATION PROGRESSION")
print("="*80)

for field, desc in intent_fields:
    analyze_field_progression(results, field, desc)

# Newer fields
newer_fields = [
    ('period_products', 'Period products bills'),
    ('incarceration', 'Incarceration-related bills')
]

print("\n" + "="*80)
print("EMERGING POLICY AREAS PROGRESSION")
print("="*80)

for field, desc in newer_fields:
    analyze_field_progression(results, field, desc)

# Summary analysis
print("\n" + "="*80)
print("SUMMARY INSIGHTS")
print("="*80)

print("\nFields with 100% Complete Data (No NULLs) Across All Years:")
complete_fields = []
for field, _ in status_fields + policy_fields + intent_fields + newer_fields:
    if results[f'{field}_null'].sum() == 0:
        complete_fields.append(field)

for field in complete_fields:
    print(f"  ✅ {field}")

print("\nFields with Improving Data Quality Over Time:")
for field, desc in status_fields + policy_fields + intent_fields + newer_fields:
    early_nulls = results[results['data_year'] <= 2010][f'{field}_null'].sum()
    early_total = results[results['data_year'] <= 2010]['total_bills'].sum()
    recent_nulls = results[results['data_year'] >= 2018][f'{field}_null'].sum()
    recent_total = results[results['data_year'] >= 2018]['total_bills'].sum()
    
    if early_total > 0 and recent_total > 0:
        early_null_pct = (early_nulls / early_total) * 100
        recent_null_pct = (recent_nulls / recent_total) * 100
        improvement = early_null_pct - recent_null_pct
        
        if improvement > 10:  # More than 10% improvement
            print(f"  📈 {field}: {early_null_pct:.1f}% → {recent_null_pct:.1f}% NULL rate")

# Export detailed results
results.to_csv('yearly_field_progression_analysis.csv', index=False)
print(f"\n💾 Detailed year-by-year data saved to: yearly_field_progression_analysis.csv")
print(f"Total years analyzed: {len(results)}")
print(f"Total bills across all years: {results['total_bills'].sum():,}")