#!/usr/bin/env python3
"""
Fix existing data to properly handle NULL vs FALSE patterns
for policy categories and intent fields.
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def analyze_current_null_patterns():
    """Analyze current NULL patterns to understand what needs fixing."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Check key fields that should have NULL patterns
    analysis_query = f"""
    SELECT 
      data_year,
      COUNT(*) as total_bills,
      
      -- Period products (should be NULL before 2019)
      SUM(CASE WHEN period_products IS NULL THEN 1 ELSE 0 END) as period_products_null,
      SUM(CASE WHEN period_products = TRUE THEN 1 ELSE 0 END) as period_products_true,
      SUM(CASE WHEN period_products = FALSE THEN 1 ELSE 0 END) as period_products_false,
      
      -- Incarceration (should be NULL before 2019)
      SUM(CASE WHEN incarceration IS NULL THEN 1 ELSE 0 END) as incarceration_null,
      SUM(CASE WHEN incarceration = TRUE THEN 1 ELSE 0 END) as incarceration_true,
      SUM(CASE WHEN incarceration = FALSE THEN 1 ELSE 0 END) as incarceration_false,
      
      -- Contraception (should be NULL 2006-2008)
      SUM(CASE WHEN contraception IS NULL THEN 1 ELSE 0 END) as contraception_null,
      SUM(CASE WHEN contraception = TRUE THEN 1 ELSE 0 END) as contraception_true,
      SUM(CASE WHEN contraception = FALSE THEN 1 ELSE 0 END) as contraception_false,
      
      -- Intent fields (should be NULL before 2006)
      SUM(CASE WHEN positive IS NULL THEN 1 ELSE 0 END) as positive_null,
      SUM(CASE WHEN positive = TRUE THEN 1 ELSE 0 END) as positive_true,
      SUM(CASE WHEN positive = FALSE THEN 1 ELSE 0 END) as positive_false
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    GROUP BY data_year
    ORDER BY data_year
    """
    
    print("🔍 ANALYZING CURRENT NULL/FALSE PATTERNS")
    print("=" * 80)
    
    results = client.query(analysis_query).result()
    
    # Focus on key problematic years
    problem_years = []
    
    for row in results:
        year = row.data_year
        total = row.total_bills
        
        # Check period products - should be NULL before 2019
        if year < 2019 and row.period_products_null == 0:
            problem_years.append(f"{year}: period_products should be NULL (currently {row.period_products_false} FALSE)")
        
        # Check incarceration - should be NULL before 2019  
        if year < 2019 and row.incarceration_null == 0:
            problem_years.append(f"{year}: incarceration should be NULL (currently {row.incarceration_false} FALSE)")
        
        # Check contraception - should be NULL 2006-2008
        if 2006 <= year <= 2008 and row.contraception_null == 0:
            problem_years.append(f"{year}: contraception should be NULL (currently {row.contraception_false} FALSE)")
        
        # Check intent fields - should be NULL before 2006
        if year < 2006 and row.positive_null == 0:
            problem_years.append(f"{year}: intent fields should be NULL (currently {row.positive_false} FALSE)")
    
    print(f"Found {len(problem_years)} issues:")
    for issue in problem_years[:10]:  # Show first 10
        print(f"  - {issue}")
    
    return len(problem_years) > 0

def create_corrected_policy_categories():
    """Create corrected policy category fields that properly handle NULL vs FALSE."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Create a view that fixes the NULL patterns based on our knowledge
    corrected_view_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.corrected_policy_tracking` AS
    SELECT 
      *,
      
      -- Fix period products (only tracked 2019+)
      CASE 
        WHEN data_year < 2019 THEN NULL
        ELSE period_products
      END as period_products_corrected,
      
      -- Fix incarceration (only tracked 2019+)
      CASE 
        WHEN data_year < 2019 THEN NULL
        ELSE incarceration
      END as incarceration_corrected,
      
      -- Fix contraception (gap 2006-2008)
      CASE 
        WHEN data_year BETWEEN 2006 AND 2008 THEN NULL
        ELSE contraception
      END as contraception_corrected,
      
      -- Fix intent fields (not tracked before 2006)
      CASE 
        WHEN data_year < 2006 THEN NULL
        ELSE positive
      END as positive_corrected,
      
      CASE 
        WHEN data_year < 2006 THEN NULL
        ELSE neutral
      END as neutral_corrected,
      
      CASE 
        WHEN data_year < 2006 THEN NULL
        WHEN data_year BETWEEN 2006 AND 2008 THEN NULL  -- Restrictive added in 2009
        ELSE restrictive
      END as restrictive_corrected,
      
      -- Fix emergency contraception (limited early tracking)
      CASE 
        WHEN data_year < 2009 THEN NULL
        ELSE emergency_contraception
      END as emergency_contraception_corrected,
      
      -- Fix pregnancy (started around 2010)
      CASE 
        WHEN data_year < 2010 THEN NULL
        ELSE pregnancy
      END as pregnancy_corrected
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    """
    
    print("\n🔄 Creating corrected policy tracking view...")
    try:
        job = client.query(corrected_view_sql)
        job.result()
        print("✅ Created corrected_policy_tracking view")
        return True
    except Exception as e:
        print(f"❌ Failed to create corrected view: {e}")
        return False

def create_consolidated_intent_field():
    """Create a consolidated intent field while preserving existing boolean fields."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Create view that adds a consolidated intent field
    intent_consolidation_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.bills_with_consolidated_intent` AS
    SELECT 
      *,
      
      -- Create consolidated intent field (single source of truth)
      CASE 
        WHEN data_year < 2006 THEN NULL  -- Intent not tracked before 2006
        WHEN positive_corrected = TRUE AND restrictive_corrected = TRUE THEN 'Mixed'
        WHEN positive_corrected = TRUE THEN 'Positive'
        WHEN restrictive_corrected = TRUE THEN 'Restrictive'  
        WHEN neutral_corrected = TRUE THEN 'Neutral'
        WHEN data_year BETWEEN 2006 AND 2008 THEN 'Unclassified'  -- Pre-restrictive era
        ELSE 'Unclassified'
      END as intent_consolidated,
      
      -- Create data quality indicators
      CASE 
        WHEN data_year < 2006 THEN 'Intent not tracked'
        WHEN data_year BETWEEN 2006 AND 2008 THEN 'Basic intent tracking (no restrictive)'
        WHEN data_year >= 2009 THEN 'Full intent tracking'
        ELSE 'Unknown'
      END as intent_tracking_era,
      
      -- Create policy tracking indicators
      CASE 
        WHEN data_year < 2019 THEN 'Period products not tracked'
        WHEN period_products_corrected = TRUE THEN 'Period products tracked and applicable'
        WHEN period_products_corrected = FALSE THEN 'Period products tracked but not applicable'
        ELSE 'Period products tracking unknown'
      END as period_products_tracking_status,
      
      CASE 
        WHEN data_year < 2019 THEN 'Incarceration not tracked'
        WHEN incarceration_corrected = TRUE THEN 'Incarceration tracked and applicable'
        WHEN incarceration_corrected = FALSE THEN 'Incarceration tracked but not applicable'
        ELSE 'Incarceration tracking unknown'
      END as incarceration_tracking_status
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.corrected_policy_tracking`
    """
    
    print("\n🔄 Creating consolidated intent view...")
    try:
        job = client.query(intent_consolidation_sql)
        job.result()
        print("✅ Created bills_with_consolidated_intent view")
        return True
    except Exception as e:
        print(f"❌ Failed to create intent consolidation view: {e}")
        return False

def test_corrected_data():
    """Test the corrected data to ensure it matches expected patterns."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Test the corrected patterns
    test_query = f"""
    SELECT 
      data_year,
      COUNT(*) as total_bills,
      
      -- Test period products correction
      SUM(CASE WHEN period_products_corrected IS NULL THEN 1 ELSE 0 END) as period_null,
      SUM(CASE WHEN period_products_corrected = TRUE THEN 1 ELSE 0 END) as period_true,
      
      -- Test incarceration correction  
      SUM(CASE WHEN incarceration_corrected IS NULL THEN 1 ELSE 0 END) as incarc_null,
      SUM(CASE WHEN incarceration_corrected = TRUE THEN 1 ELSE 0 END) as incarc_true,
      
      -- Test contraception correction
      SUM(CASE WHEN contraception_corrected IS NULL THEN 1 ELSE 0 END) as contra_null,
      SUM(CASE WHEN contraception_corrected = TRUE THEN 1 ELSE 0 END) as contra_true,
      
      -- Test intent consolidation
      SUM(CASE WHEN intent_consolidated IS NULL THEN 1 ELSE 0 END) as intent_null,
      SUM(CASE WHEN intent_consolidated = 'Positive' THEN 1 ELSE 0 END) as intent_positive,
      SUM(CASE WHEN intent_consolidated = 'Restrictive' THEN 1 ELSE 0 END) as intent_restrictive,
      SUM(CASE WHEN intent_consolidated = 'Mixed' THEN 1 ELSE 0 END) as intent_mixed
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.bills_with_consolidated_intent`
    WHERE data_year IN (2002, 2007, 2016, 2019, 2023)
    GROUP BY data_year
    ORDER BY data_year
    """
    
    print("\n📊 TESTING CORRECTED DATA")
    print("=" * 80)
    
    results = client.query(test_query).result()
    
    print(f"{'Year':<6} {'Bills':<6} {'Period':<15} {'Incarc':<15} {'Contra':<15} {'Intent':<20}")
    print("-" * 80)
    
    for row in results:
        period_status = f"NULL:{row.period_null} TRUE:{row.period_true}"
        incarc_status = f"NULL:{row.incarc_null} TRUE:{row.incarc_true}"
        contra_status = f"NULL:{row.contra_null} TRUE:{row.contra_true}"
        intent_status = f"NULL:{row.intent_null} POS:{row.intent_positive} REST:{row.intent_restrictive}"
        
        print(f"{row.data_year:<6} {row.total_bills:<6} {period_status:<15} {incarc_status:<15} {contra_status:<15} {intent_status:<20}")

if __name__ == "__main__":
    print("🔧 FIXING NULL/FALSE PATTERNS IN HISTORICAL DATA")
    print("=" * 70)
    
    # Step 1: Analyze current patterns
    has_issues = analyze_current_null_patterns()
    
    if has_issues:
        print(f"\n⚠️  Issues found - creating corrected views...")
        
        # Step 2: Create corrected policy tracking
        if create_corrected_policy_categories():
            print("✅ Policy categories corrected")
        
        # Step 3: Create consolidated intent field
        if create_consolidated_intent_field():
            print("✅ Intent field consolidated")
        
        # Step 4: Test the corrections
        test_corrected_data()
        
        print(f"\n✅ CORRECTIONS COMPLETE")
        print(f"Use 'bills_with_consolidated_intent' view for corrected data")
        print(f"This preserves your existing dashboard structure while fixing NULL patterns")
    else:
        print(f"\n✅ No issues found - data patterns are correct")