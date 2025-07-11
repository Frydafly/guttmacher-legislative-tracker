from google.cloud import bigquery
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

# Query to analyze field consistency across all years
query = """
WITH field_analysis AS (
  SELECT 
    'all_years' as analysis_period,
    COUNT(*) as total_records,
    
    -- Basic fields
    COUNTIF(state IS NOT NULL) / COUNT(*) * 100 as state_pct,
    COUNTIF(bill_number IS NOT NULL) / COUNT(*) * 100 as bill_number_pct,
    COUNTIF(bill_type IS NOT NULL) / COUNT(*) * 100 as bill_type_pct,
    COUNTIF(description IS NOT NULL) / COUNT(*) * 100 as description_pct,
    COUNTIF(internal_summary IS NOT NULL) / COUNT(*) * 100 as internal_summary_pct,
    
    -- Date fields
    COUNTIF(introduced_date IS NOT NULL) / COUNT(*) * 100 as introduced_date_pct,
    COUNTIF(last_action_date IS NOT NULL) / COUNT(*) * 100 as last_action_date_pct,
    COUNTIF(effective_date IS NOT NULL) / COUNT(*) * 100 as effective_date_pct,
    COUNTIF(enacted_date IS NOT NULL) / COUNT(*) * 100 as enacted_date_pct,
    
    -- Status fields (should be mostly 100% due to FALSE defaults)
    COUNTIF(introduced IS NOT NULL) / COUNT(*) * 100 as introduced_pct,
    COUNTIF(enacted IS NOT NULL) / COUNT(*) * 100 as enacted_pct,
    COUNTIF(vetoed IS NOT NULL) / COUNT(*) * 100 as vetoed_pct,
    COUNTIF(dead IS NOT NULL) / COUNT(*) * 100 as dead_pct,
    COUNTIF(pending IS NOT NULL) / COUNT(*) * 100 as pending_pct,
    COUNTIF(passed_first_chamber IS NOT NULL) / COUNT(*) * 100 as passed_first_chamber_pct,
    COUNTIF(passed_second_chamber IS NOT NULL) / COUNT(*) * 100 as passed_second_chamber_pct,
    COUNTIF(seriously_considered IS NOT NULL) / COUNT(*) * 100 as seriously_considered_pct,
    
    -- Core policy categories
    COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100 as abortion_pct,
    COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100 as contraception_pct,
    COUNTIF(minors IS NOT NULL) / COUNT(*) * 100 as minors_pct,
    COUNTIF(sex_education IS NOT NULL) / COUNT(*) * 100 as sex_education_pct,
    COUNTIF(insurance IS NOT NULL) / COUNT(*) * 100 as insurance_pct,
    
    -- Intent fields
    COUNTIF(positive IS NOT NULL) / COUNT(*) * 100 as positive_pct,
    COUNTIF(neutral IS NOT NULL) / COUNT(*) * 100 as neutral_pct,
    COUNTIF(restrictive IS NOT NULL) / COUNT(*) * 100 as restrictive_pct,
    
    -- Other categories
    COUNTIF(emergency_contraception IS NOT NULL) / COUNT(*) * 100 as emergency_contraception_pct,
    COUNTIF(pregnancy IS NOT NULL) / COUNT(*) * 100 as pregnancy_pct,
    COUNTIF(stis IS NOT NULL) / COUNT(*) * 100 as stis_pct,
    COUNTIF(appropriations IS NOT NULL) / COUNT(*) * 100 as appropriations_pct,
    COUNTIF(incarceration IS NOT NULL) / COUNT(*) * 100 as incarceration_pct,
    COUNTIF(period_products IS NOT NULL) / COUNT(*) * 100 as period_products_pct,
    COUNTIF(fetal_issues IS NOT NULL) / COUNT(*) * 100 as fetal_issues_pct,
    COUNTIF(fetal_tissue IS NOT NULL) / COUNT(*) * 100 as fetal_tissue_pct,
    COUNTIF(refusal IS NOT NULL) / COUNT(*) * 100 as refusal_pct
    
  FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
)
SELECT * FROM field_analysis

UNION ALL

-- Year-by-year breakdown
SELECT 
  CAST(data_year AS STRING) as analysis_period,
  COUNT(*) as total_records,
  
  -- Basic fields
  COUNTIF(state IS NOT NULL) / COUNT(*) * 100 as state_pct,
  COUNTIF(bill_number IS NOT NULL) / COUNT(*) * 100 as bill_number_pct,
  COUNTIF(bill_type IS NOT NULL) / COUNT(*) * 100 as bill_type_pct,
  COUNTIF(description IS NOT NULL) / COUNT(*) * 100 as description_pct,
  COUNTIF(internal_summary IS NOT NULL) / COUNT(*) * 100 as internal_summary_pct,
  
  -- Date fields
  COUNTIF(introduced_date IS NOT NULL) / COUNT(*) * 100 as introduced_date_pct,
  COUNTIF(last_action_date IS NOT NULL) / COUNT(*) * 100 as last_action_date_pct,
  COUNTIF(effective_date IS NOT NULL) / COUNT(*) * 100 as effective_date_pct,
  COUNTIF(enacted_date IS NOT NULL) / COUNT(*) * 100 as enacted_date_pct,
  
  -- Status fields
  COUNTIF(introduced IS NOT NULL) / COUNT(*) * 100 as introduced_pct,
  COUNTIF(enacted IS NOT NULL) / COUNT(*) * 100 as enacted_pct,
  COUNTIF(vetoed IS NOT NULL) / COUNT(*) * 100 as vetoed_pct,
  COUNTIF(dead IS NOT NULL) / COUNT(*) * 100 as dead_pct,
  COUNTIF(pending IS NOT NULL) / COUNT(*) * 100 as pending_pct,
  COUNTIF(passed_first_chamber IS NOT NULL) / COUNT(*) * 100 as passed_first_chamber_pct,
  COUNTIF(passed_second_chamber IS NOT NULL) / COUNT(*) * 100 as passed_second_chamber_pct,
  COUNTIF(seriously_considered IS NOT NULL) / COUNT(*) * 100 as seriously_considered_pct,
  
  -- Core policy categories
  COUNTIF(abortion IS NOT NULL) / COUNT(*) * 100 as abortion_pct,
  COUNTIF(contraception IS NOT NULL) / COUNT(*) * 100 as contraception_pct,
  COUNTIF(minors IS NOT NULL) / COUNT(*) * 100 as minors_pct,
  COUNTIF(sex_education IS NOT NULL) / COUNT(*) * 100 as sex_education_pct,
  COUNTIF(insurance IS NOT NULL) / COUNT(*) * 100 as insurance_pct,
  
  -- Intent fields
  COUNTIF(positive IS NOT NULL) / COUNT(*) * 100 as positive_pct,
  COUNTIF(neutral IS NOT NULL) / COUNT(*) * 100 as neutral_pct,
  COUNTIF(restrictive IS NOT NULL) / COUNT(*) * 100 as restrictive_pct,
  
  -- Other categories
  COUNTIF(emergency_contraception IS NOT NULL) / COUNT(*) * 100 as emergency_contraception_pct,
  COUNTIF(pregnancy IS NOT NULL) / COUNT(*) * 100 as pregnancy_pct,
  COUNTIF(stis IS NOT NULL) / COUNT(*) * 100 as stis_pct,
  COUNTIF(appropriations IS NOT NULL) / COUNT(*) * 100 as appropriations_pct,
  COUNTIF(incarceration IS NOT NULL) / COUNT(*) * 100 as incarceration_pct,
  COUNTIF(period_products IS NOT NULL) / COUNT(*) * 100 as period_products_pct,
  COUNTIF(fetal_issues IS NOT NULL) / COUNT(*) * 100 as fetal_issues_pct,
  COUNTIF(fetal_tissue IS NOT NULL) / COUNT(*) * 100 as fetal_tissue_pct,
  COUNTIF(refusal IS NOT NULL) / COUNT(*) * 100 as refusal_pct

FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
GROUP BY data_year
ORDER BY analysis_period
""".replace("{project}", os.getenv('GCP_PROJECT_ID'))

print("Analyzing field consistency across all years...")
print("=" * 80)

# Run the query
results = client.query(query).to_dataframe()

# Transpose for better readability
all_years_data = results[results['analysis_period'] == 'all_years'].iloc[0]
yearly_data = results[results['analysis_period'] != 'all_years']

print("\n📊 OVERALL FIELD CONSISTENCY (All Years Combined)")
print("-" * 50)

# Sort fields by consistency percentage
field_consistency = []
for col in results.columns:
    if col.endswith('_pct'):
        field_name = col.replace('_pct', '')
        consistency = all_years_data[col]
        field_consistency.append((field_name, consistency))

field_consistency.sort(key=lambda x: x[1], reverse=True)

print("\nMost Consistent Fields (>95% populated):")
for field, pct in field_consistency:
    if pct > 95:
        print(f"  ✅ {field}: {pct:.1f}%")

print("\nModerately Consistent Fields (50-95% populated):")
for field, pct in field_consistency:
    if 50 <= pct <= 95:
        print(f"  ⚠️  {field}: {pct:.1f}%")

print("\nRarely Populated Fields (<50% populated):")
for field, pct in field_consistency:
    if pct < 50:
        print(f"  ❌ {field}: {pct:.1f}%")

# Year-over-year consistency analysis
print("\n\n📈 YEAR-OVER-YEAR CONSISTENCY TRENDS")
print("-" * 50)

# Identify fields that became more consistent over time
print("\nFields with Improving Consistency:")
for col in results.columns:
    if col.endswith('_pct'):
        field_name = col.replace('_pct', '')
        early_years = yearly_data[yearly_data['analysis_period'].astype(int) <= 2010][col].mean()
        recent_years = yearly_data[yearly_data['analysis_period'].astype(int) >= 2015][col].mean()
        
        if recent_years - early_years > 20:  # More than 20% improvement
            print(f"  📈 {field_name}: {early_years:.1f}% (2002-2010) → {recent_years:.1f}% (2015+)")

# Export detailed results
results.to_csv('field_consistency_analysis.csv', index=False)
print(f"\n\n💾 Detailed results saved to: field_consistency_analysis.csv")
print(f"Total records analyzed: {int(all_years_data['total_records']):,}")