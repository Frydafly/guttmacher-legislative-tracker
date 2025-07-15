#!/usr/bin/env python3
"""
Create comprehensive field tracking analysis that clearly shows:
1. Was this field tracked at all this year? (NULL vs NOT NULL)
2. If tracked, what was the data quality/completeness?
3. Different expectations for different field types
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def analyze_field_tracking():
    """Create comprehensive field tracking analysis."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Get all field names from the unified view
    schema_query = f"""
    SELECT column_name, data_type
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'all_historical_bills_unified'
    AND column_name NOT IN ('id', 'data_year') -- Skip these system fields
    ORDER BY column_name
    """
    
    results = client.query(schema_query).result()
    fields = [(row.column_name, row.data_type) for row in results]
    
    print(f"Analyzing {len(fields)} fields across all years...")
    
    # Create comprehensive tracking analysis
    tracking_analysis_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_tracking_completeness_by_year` AS
    SELECT 
      data_year,
      COUNT(*) as total_bills,
      
      -- CORE IDENTIFICATION FIELDS (should always be tracked)
      ROUND(SUM(CASE WHEN `state` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as state_tracking_pct,
      ROUND(SUM(CASE WHEN `bill_number` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as bill_number_tracking_pct,
      ROUND(SUM(CASE WHEN `description` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as description_tracking_pct,
      
      -- BILL CLASSIFICATION FIELDS (tracking evolved over time)
      ROUND(SUM(CASE WHEN `bill_type` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as bill_type_tracking_pct,
      ROUND(SUM(CASE WHEN `history` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as history_tracking_pct,
      ROUND(SUM(CASE WHEN `notes` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as notes_tracking_pct,
      ROUND(SUM(CASE WHEN `website_blurb` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as website_blurb_tracking_pct,
      ROUND(SUM(CASE WHEN `internal_summary` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as internal_summary_tracking_pct,
      
      -- DATE FIELDS (tracking began at different times)
      ROUND(SUM(CASE WHEN `introduced_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as introduced_date_tracking_pct,
      ROUND(SUM(CASE WHEN `last_action_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as last_action_date_tracking_pct,
      ROUND(SUM(CASE WHEN `effective_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as effective_date_tracking_pct,
      ROUND(SUM(CASE WHEN `enacted_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as enacted_date_tracking_pct,
      
      -- STATUS FIELDS (boolean tracking - critical to distinguish NULL vs FALSE)
      ROUND(SUM(CASE WHEN `introduced` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as introduced_status_tracking_pct,
      ROUND(SUM(CASE WHEN `seriously_considered` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as seriously_considered_tracking_pct,
      ROUND(SUM(CASE WHEN `passed_first_chamber` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as passed_first_chamber_tracking_pct,
      ROUND(SUM(CASE WHEN `passed_second_chamber` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as passed_second_chamber_tracking_pct,
      ROUND(SUM(CASE WHEN `enacted` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as enacted_status_tracking_pct,
      ROUND(SUM(CASE WHEN `vetoed` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as vetoed_status_tracking_pct,
      ROUND(SUM(CASE WHEN `dead` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as dead_status_tracking_pct,
      ROUND(SUM(CASE WHEN `pending` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as pending_status_tracking_pct,
      
      -- INTENT FIELDS (boolean tracking - evolved over time)
      ROUND(SUM(CASE WHEN `positive` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as positive_intent_tracking_pct,
      ROUND(SUM(CASE WHEN `neutral` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as neutral_intent_tracking_pct,
      ROUND(SUM(CASE WHEN `restrictive` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as restrictive_intent_tracking_pct,
      
      -- POLICY CATEGORY FIELDS (boolean tracking - evolved significantly)
      ROUND(SUM(CASE WHEN `abortion` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as abortion_tracking_pct,
      ROUND(SUM(CASE WHEN `contraception` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as contraception_tracking_pct,
      ROUND(SUM(CASE WHEN `emergency_contraception` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as emergency_contraception_tracking_pct,
      ROUND(SUM(CASE WHEN `minors` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as minors_tracking_pct,
      ROUND(SUM(CASE WHEN `pregnancy` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as pregnancy_tracking_pct,
      ROUND(SUM(CASE WHEN `refusal` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as refusal_tracking_pct,
      ROUND(SUM(CASE WHEN `sex_education` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as sex_education_tracking_pct,
      ROUND(SUM(CASE WHEN `insurance` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as insurance_tracking_pct,
      ROUND(SUM(CASE WHEN `appropriations` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as appropriations_tracking_pct,
      ROUND(SUM(CASE WHEN `fetal_issues` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as fetal_issues_tracking_pct,
      ROUND(SUM(CASE WHEN `fetal_tissue` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as fetal_tissue_tracking_pct,
      ROUND(SUM(CASE WHEN `incarceration` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as incarceration_tracking_pct,
      ROUND(SUM(CASE WHEN `period_products` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as period_products_tracking_pct,
      ROUND(SUM(CASE WHEN `stis` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as stis_tracking_pct,
      
      -- TRACKING QUALITY INDICATORS
      CASE 
        WHEN data_year <= 2005 THEN 'Foundation Era - Basic Tracking'
        WHEN data_year <= 2015 THEN 'Revolution Era - Modern Status Tracking'
        WHEN data_year <= 2018 THEN 'Comprehensive Era - Full Date Tracking'
        ELSE 'Modern Era - Rich Summaries'
      END as tracking_era,
      
      -- CRITICAL GAPS DETECTION
      CASE 
        WHEN SUM(CASE WHEN `introduced` IS NOT NULL THEN 1 ELSE 0 END) = 0 THEN 'NO STATUS TRACKING'
        WHEN SUM(CASE WHEN `abortion` IS NOT NULL THEN 1 ELSE 0 END) = 0 THEN 'NO POLICY TRACKING'
        WHEN SUM(CASE WHEN `positive` IS NOT NULL THEN 1 ELSE 0 END) = 0 AND data_year >= 2006 THEN 'NO INTENT TRACKING'
        ELSE 'TRACKING ACTIVE'
      END as tracking_status

    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    GROUP BY data_year
    ORDER BY data_year
    """
    
    print("Creating comprehensive field tracking analysis view...")
    try:
        job = client.query(tracking_analysis_sql)
        job.result()
        print("✅ Created field_tracking_completeness_by_year view")
    except Exception as e:
        print(f"❌ Failed to create tracking analysis: {e}")
        return
    
    # Test the view and create a summary report
    test_query = f"""
    SELECT 
      data_year,
      total_bills,
      tracking_era,
      tracking_status,
      -- Core fields (should always be near 100%)
      state_tracking_pct,
      bill_number_tracking_pct,
      description_tracking_pct,
      -- Key evolution fields
      bill_type_tracking_pct,
      introduced_date_tracking_pct,
      internal_summary_tracking_pct,
      -- Status tracking (critical for analysis)
      introduced_status_tracking_pct,
      enacted_status_tracking_pct,
      -- Intent tracking (evolved over time)
      positive_intent_tracking_pct,
      restrictive_intent_tracking_pct,
      -- Policy categories (core ones)
      abortion_tracking_pct,
      contraception_tracking_pct,
      minors_tracking_pct,
      -- Emerging categories
      period_products_tracking_pct,
      incarceration_tracking_pct
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_tracking_completeness_by_year`
    ORDER BY data_year
    """
    
    print("\n📊 FIELD TRACKING COMPLETENESS ANALYSIS")
    print("=" * 80)
    
    results = client.query(test_query).result()
    
    # Convert to DataFrame for better analysis
    df = pd.DataFrame([dict(row) for row in results])
    
    print(f"\n🔍 SUMMARY BY ERA:")
    print("-" * 50)
    
    for era in df['tracking_era'].unique():
        era_data = df[df['tracking_era'] == era]
        years = f"{era_data['data_year'].min()}-{era_data['data_year'].max()}"
        bills = era_data['total_bills'].sum()
        print(f"\n{era} ({years}): {bills:,} bills")
        
        # Check for critical gaps
        if any(era_data['tracking_status'] != 'TRACKING ACTIVE'):
            problem_years = era_data[era_data['tracking_status'] != 'TRACKING ACTIVE']['data_year'].tolist()
            print(f"  ⚠️  GAPS: {problem_years}")
        
        # Show key tracking percentages
        avg_abortion = era_data['abortion_tracking_pct'].mean()
        avg_contraception = era_data['contraception_tracking_pct'].mean()
        avg_status = era_data['introduced_status_tracking_pct'].mean()
        avg_intent = era_data['positive_intent_tracking_pct'].mean()
        
        print(f"  📈 Abortion: {avg_abortion:.0f}% | Contraception: {avg_contraception:.0f}% | Status: {avg_status:.0f}% | Intent: {avg_intent:.0f}%")

def create_field_evolution_report():
    """Create a detailed field evolution report."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Create a detailed field evolution matrix
    evolution_query = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_evolution_matrix` AS
    SELECT 
      data_year,
      total_bills,
      
      -- Show tracking status for each field as clear indicators
      CASE 
        WHEN ROUND(SUM(CASE WHEN `state` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `state` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as state_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `bill_type` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `bill_type` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as bill_type_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `introduced_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `introduced_date` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as introduced_date_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `internal_summary` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `internal_summary` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as internal_summary_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `introduced` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `introduced` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as status_tracking_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `positive` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `positive` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as intent_tracking_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `abortion` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `abortion` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as abortion_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `contraception` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `contraception` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as contraception_status,
      
      CASE 
        WHEN ROUND(SUM(CASE WHEN `period_products` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 95 THEN '✅ TRACKED'
        WHEN ROUND(SUM(CASE WHEN `period_products` IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) >= 50 THEN '⚠️ PARTIAL'
        ELSE '❌ NOT TRACKED'
      END as period_products_status
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified`
    GROUP BY data_year
    ORDER BY data_year
    """
    
    print("\n🔄 Creating field evolution matrix...")
    try:
        job = client.query(evolution_query)
        job.result()
        print("✅ Created field_evolution_matrix view")
    except Exception as e:
        print(f"❌ Failed to create evolution matrix: {e}")
        return
    
    # Display the matrix
    test_query = f"""
    SELECT * FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.field_evolution_matrix`
    ORDER BY data_year
    """
    
    print("\n📋 FIELD EVOLUTION MATRIX")
    print("=" * 120)
    print(f"{'Year':<6} {'Bills':<6} {'State':<12} {'BillType':<12} {'IntroDate':<12} {'Summary':<12} {'Status':<12} {'Intent':<12} {'Abortion':<12} {'Contra':<12} {'Period':<12}")
    print("-" * 120)
    
    results = client.query(test_query).result()
    for row in results:
        print(f"{row.data_year:<6} {row.total_bills:<6} {row.state_status:<12} {row.bill_type_status:<12} {row.introduced_date_status:<12} {row.internal_summary_status:<12} {row.status_tracking_status:<12} {row.intent_tracking_status:<12} {row.abortion_status:<12} {row.contraception_status:<12} {row.period_products_status:<12}")

if __name__ == "__main__":
    print("🔍 CREATING COMPREHENSIVE FIELD TRACKING ANALYSIS")
    print("=" * 70)
    
    analyze_field_tracking()
    create_field_evolution_report()
    
    print("\n✅ ANALYSIS COMPLETE")
    print("\nCreated views:")
    print("- field_tracking_completeness_by_year: Detailed tracking percentages")
    print("- field_evolution_matrix: Visual tracking status matrix")
    print("\nUse these views to understand:")
    print("1. What fields were tracked each year")
    print("2. Data quality vs tracking completeness")
    print("3. Evolution of tracking methodology over time")