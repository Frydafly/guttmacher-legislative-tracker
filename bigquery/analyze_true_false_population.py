from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

# Query to analyze TRUE/FALSE vs NULL rates
query = """
WITH field_analysis AS (
  SELECT 
    'all_years' as analysis_period,
    COUNT(*) as total_records,
    
    -- Status fields - TRUE/FALSE rates
    COUNTIF(introduced = TRUE) / COUNT(*) * 100 as introduced_true_pct,
    COUNTIF(introduced = FALSE) / COUNT(*) * 100 as introduced_false_pct,
    COUNTIF(enacted = TRUE) / COUNT(*) * 100 as enacted_true_pct,
    COUNTIF(enacted = FALSE) / COUNT(*) * 100 as enacted_false_pct,
    COUNTIF(vetoed = TRUE) / COUNT(*) * 100 as vetoed_true_pct,
    COUNTIF(vetoed = FALSE) / COUNT(*) * 100 as vetoed_false_pct,
    COUNTIF(dead = TRUE) / COUNT(*) * 100 as dead_true_pct,
    COUNTIF(dead = FALSE) / COUNT(*) * 100 as dead_false_pct,
    COUNTIF(pending = TRUE) / COUNT(*) * 100 as pending_true_pct,
    COUNTIF(pending = FALSE) / COUNT(*) * 100 as pending_false_pct,
    COUNTIF(passed_first_chamber = TRUE) / COUNT(*) * 100 as passed_first_chamber_true_pct,
    COUNTIF(passed_first_chamber = FALSE) / COUNT(*) * 100 as passed_first_chamber_false_pct,
    COUNTIF(passed_second_chamber = TRUE) / COUNT(*) * 100 as passed_second_chamber_true_pct,
    COUNTIF(passed_second_chamber = FALSE) / COUNT(*) * 100 as passed_second_chamber_false_pct,
    COUNTIF(seriously_considered = TRUE) / COUNT(*) * 100 as seriously_considered_true_pct,
    COUNTIF(seriously_considered = FALSE) / COUNT(*) * 100 as seriously_considered_false_pct,
    
    -- Policy categories - TRUE vs NULL rates (FALSE would be very rare)
    COUNTIF(abortion = TRUE) / COUNT(*) * 100 as abortion_true_pct,
    COUNTIF(abortion IS NULL) / COUNT(*) * 100 as abortion_null_pct,
    COUNTIF(contraception = TRUE) / COUNT(*) * 100 as contraception_true_pct,
    COUNTIF(contraception IS NULL) / COUNT(*) * 100 as contraception_null_pct,
    COUNTIF(minors = TRUE) / COUNT(*) * 100 as minors_true_pct,
    COUNTIF(minors IS NULL) / COUNT(*) * 100 as minors_null_pct,
    COUNTIF(sex_education = TRUE) / COUNT(*) * 100 as sex_education_true_pct,
    COUNTIF(sex_education IS NULL) / COUNT(*) * 100 as sex_education_null_pct,
    COUNTIF(insurance = TRUE) / COUNT(*) * 100 as insurance_true_pct,
    COUNTIF(insurance IS NULL) / COUNT(*) * 100 as insurance_null_pct,
    COUNTIF(emergency_contraception = TRUE) / COUNT(*) * 100 as emergency_contraception_true_pct,
    COUNTIF(emergency_contraception IS NULL) / COUNT(*) * 100 as emergency_contraception_null_pct,
    COUNTIF(pregnancy = TRUE) / COUNT(*) * 100 as pregnancy_true_pct,
    COUNTIF(pregnancy IS NULL) / COUNT(*) * 100 as pregnancy_null_pct,
    COUNTIF(appropriations = TRUE) / COUNT(*) * 100 as appropriations_true_pct,
    COUNTIF(appropriations IS NULL) / COUNT(*) * 100 as appropriations_null_pct,
    
    -- Intent fields - TRUE vs NULL rates
    COUNTIF(positive = TRUE) / COUNT(*) * 100 as positive_true_pct,
    COUNTIF(positive IS NULL) / COUNT(*) * 100 as positive_null_pct,
    COUNTIF(neutral = TRUE) / COUNT(*) * 100 as neutral_true_pct,
    COUNTIF(neutral IS NULL) / COUNT(*) * 100 as neutral_null_pct,
    COUNTIF(restrictive = TRUE) / COUNT(*) * 100 as restrictive_true_pct,
    COUNTIF(restrictive IS NULL) / COUNT(*) * 100 as restrictive_null_pct,
    
    -- Newer categories
    COUNTIF(period_products = TRUE) / COUNT(*) * 100 as period_products_true_pct,
    COUNTIF(period_products IS NULL) / COUNT(*) * 100 as period_products_null_pct,
    COUNTIF(incarceration = TRUE) / COUNT(*) * 100 as incarceration_true_pct,
    COUNTIF(incarceration IS NULL) / COUNT(*) * 100 as incarceration_null_pct
    
  FROM `{project}.legislative_tracker_historical.all_historical_bills_unified`
)
SELECT * FROM field_analysis
""".replace("{project}", os.getenv('GCP_PROJECT_ID'))

print("Analyzing TRUE/FALSE population vs NULL rates...")
print("=" * 80)

# Run the query
results = client.query(query).to_dataframe()
data = results.iloc[0]

print("\n📊 STATUS FIELDS ANALYSIS")
print("-" * 50)

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

print("High Activity Status Fields (>5% TRUE rate):")
for field, desc in status_fields:
    true_pct = data[f'{field}_true_pct']
    false_pct = data[f'{field}_false_pct']
    if true_pct > 5:
        print(f"  ✅ {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE - {desc}")

print("\nLow Activity Status Fields (<5% TRUE rate):")
for field, desc in status_fields:
    true_pct = data[f'{field}_true_pct']
    false_pct = data[f'{field}_false_pct']
    if true_pct <= 5:
        print(f"  ⚠️  {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE - {desc}")

print("\n\n📊 POLICY CATEGORY ANALYSIS")
print("-" * 50)

policy_fields = [
    ('abortion', 'Abortion-related'),
    ('contraception', 'Contraception/birth control'),
    ('minors', 'Minors/teen issues'),
    ('sex_education', 'Sex education'),
    ('insurance', 'Insurance coverage'),
    ('emergency_contraception', 'Emergency contraception'),
    ('pregnancy', 'Pregnancy-related'),
    ('appropriations', 'Funding/appropriations')
]

print("High Coverage Policy Areas (>10% TRUE rate):")
for field, desc in policy_fields:
    true_pct = data[f'{field}_true_pct']
    null_pct = data[f'{field}_null_pct']
    false_pct = 100 - true_pct - null_pct
    if true_pct > 10:
        print(f"  ✅ {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE, {null_pct:.1f}% NULL - {desc}")

print("\nModerate Coverage Policy Areas (3-10% TRUE rate):")
for field, desc in policy_fields:
    true_pct = data[f'{field}_true_pct']
    null_pct = data[f'{field}_null_pct']
    false_pct = 100 - true_pct - null_pct
    if 3 <= true_pct <= 10:
        print(f"  ⚠️  {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE, {null_pct:.1f}% NULL - {desc}")

print("\nLow Coverage Policy Areas (<3% TRUE rate):")
for field, desc in policy_fields:
    true_pct = data[f'{field}_true_pct']
    null_pct = data[f'{field}_null_pct']
    false_pct = 100 - true_pct - null_pct
    if true_pct < 3:
        print(f"  ❌ {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE, {null_pct:.1f}% NULL - {desc}")

print("\n\n📊 INTENT CLASSIFICATION ANALYSIS")
print("-" * 50)

intent_fields = [
    ('positive', 'Pro-reproductive rights'),
    ('neutral', 'Neutral impact'),
    ('restrictive', 'Restricts reproductive rights')
]

for field, desc in intent_fields:
    true_pct = data[f'{field}_true_pct']
    null_pct = data[f'{field}_null_pct']
    false_pct = 100 - true_pct - null_pct
    print(f"  📊 {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE, {null_pct:.1f}% NULL - {desc}")

classified_pct = data['positive_true_pct'] + data['neutral_true_pct'] + data['restrictive_true_pct']
print(f"\n  📈 Total Intent Classified: {classified_pct:.1f}% of all bills")

print("\n\n📊 NEWER POLICY AREAS")
print("-" * 50)

newer_fields = [
    ('period_products', 'Period products'),
    ('incarceration', 'Incarceration-related')
]

for field, desc in newer_fields:
    true_pct = data[f'{field}_true_pct']
    null_pct = data[f'{field}_null_pct']
    false_pct = 100 - true_pct - null_pct
    print(f"  📊 {field}: {true_pct:.1f}% TRUE, {false_pct:.1f}% FALSE, {null_pct:.1f}% NULL - {desc}")

print(f"\n\n💾 Analysis complete!")
print(f"Total records analyzed: {int(data['total_records']):,}")

# Export results
results.to_csv('true_false_population_analysis.csv', index=False)
print(f"Detailed results saved to: true_false_population_analysis.csv")