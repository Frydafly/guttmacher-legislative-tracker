#!/usr/bin/env python3
"""
Update the comprehensive_bills_authentic view to use corrected data
while preserving existing structure for dashboard compatibility.
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()

def update_comprehensive_view():
    """Update comprehensive view to use corrected data while preserving structure."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Create updated comprehensive view that uses corrected data
    updated_comprehensive_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic` AS
    SELECT 
      -- Unique identifiers (preserve existing structure)
      CONCAT(CAST(data_year AS STRING), '_', state, '_', COALESCE(bill_number, 'UNKNOWN')) as unique_bill_id,
      data_year,
      
      -- Geographic info (preserve existing structure)
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
      
      -- Basic bill info (preserve existing structure)
      bill_number,
      description,
      bill_type,
      history,
      notes,
      website_blurb,
      internal_summary,
      
      -- Date fields (preserve existing structure)
      introduced_date,
      last_action_date,
      effective_date,
      enacted_date,
      
      -- Status fields (preserve existing structure - these are correctly FALSE when not tracked)
      introduced,
      seriously_considered,
      passed_first_chamber,
      passed_second_chamber,
      enacted,
      vetoed,
      dead,
      pending,
      
      -- CORRECTED INTENT FIELDS (preserve existing boolean structure but use corrected data)
      positive_corrected as positive,
      neutral_corrected as neutral,
      restrictive_corrected as restrictive,
      
      -- CORRECTED POLICY CATEGORIES (preserve existing boolean structure but use corrected data)
      abortion,  -- This was always tracked correctly
      contraception_corrected as contraception,
      emergency_contraception_corrected as emergency_contraception,
      minors,  -- This was mostly correct
      pregnancy_corrected as pregnancy,
      refusal,  -- This was mostly correct
      sex_education,  -- This was mostly correct
      insurance,  -- This was mostly correct
      appropriations,  -- This was mostly correct
      fetal_issues,  -- This was mostly correct
      fetal_tissue,  -- This was mostly correct
      incarceration_corrected as incarceration,
      period_products_corrected as period_products,
      stis,  -- This was mostly correct
      
      -- NEW CONSOLIDATED INTENT FIELD (single source of truth)
      intent_consolidated,
      intent_tracking_era,
      
      -- NEW POLICY TRACKING STATUS FIELDS
      period_products_tracking_status,
      incarceration_tracking_status,
      
      -- Calculated helper fields for dashboards (preserve existing structure)
      CASE 
        WHEN data_year >= 2019 THEN 'Modern Era (2019+)'
        WHEN data_year >= 2016 THEN 'Comprehensive Era (2016-2018)' 
        WHEN data_year >= 2006 THEN 'Methodology Revolution (2006-2015)'
        ELSE 'Foundation Era (2002-2005)'
      END as data_era,
      
      -- UPDATED STATUS SUMMARY (preserve existing structure)
      CASE 
        WHEN enacted = TRUE THEN 'Enacted'
        WHEN vetoed = TRUE THEN 'Vetoed'
        WHEN dead = TRUE THEN 'Failed/Dead'
        WHEN pending = TRUE THEN 'Pending'
        WHEN introduced = TRUE THEN 'Introduced Only'
        WHEN data_year <= 2005 THEN 'Pre-Modern Tracking'
        ELSE 'Unknown Status'
      END as status_summary,
      
      -- UPDATED INTENT SUMMARY (use consolidated field but preserve structure)
      CASE 
        WHEN intent_consolidated = 'Mixed' THEN 'Mixed Intent'
        WHEN intent_consolidated = 'Positive' THEN 'Positive/Pro-Choice'
        WHEN intent_consolidated = 'Restrictive' THEN 'Restrictive'
        WHEN intent_consolidated = 'Neutral' THEN 'Neutral'
        WHEN intent_consolidated IS NULL THEN 'Pre-Intent Tracking'
        ELSE 'Unclassified'
      END as intent_summary,
      
      -- UPDATED POLICY AREA COUNT (use corrected fields)
      (CASE WHEN abortion = TRUE THEN 1 ELSE 0 END +
       CASE WHEN contraception_corrected = TRUE THEN 1 ELSE 0 END +
       CASE WHEN emergency_contraception_corrected = TRUE THEN 1 ELSE 0 END +
       CASE WHEN minors = TRUE THEN 1 ELSE 0 END +
       CASE WHEN pregnancy_corrected = TRUE THEN 1 ELSE 0 END +
       CASE WHEN sex_education = TRUE THEN 1 ELSE 0 END +
       CASE WHEN insurance = TRUE THEN 1 ELSE 0 END +
       CASE WHEN appropriations = TRUE THEN 1 ELSE 0 END +
       CASE WHEN period_products_corrected = TRUE THEN 1 ELSE 0 END +
       CASE WHEN incarceration_corrected = TRUE THEN 1 ELSE 0 END) as policy_area_count,
      
      -- Data quality indicators (preserve existing structure)
      CASE WHEN introduced_date IS NULL THEN 'No Date Tracking' ELSE 'Has Date Tracking' END as date_tracking_era,
      CASE WHEN bill_type IS NULL THEN 'No Type Classification' ELSE 'Has Type Classification' END as type_tracking_era,
      CASE WHEN positive_corrected IS NULL AND neutral_corrected IS NULL AND restrictive_corrected IS NULL THEN 'No Intent Classification' ELSE 'Has Intent Classification' END as intent_tracking_era_legacy,
      
      -- Recent vs historical (preserve existing structure)
      CASE WHEN data_year >= 2020 THEN TRUE ELSE FALSE END as is_recent,
      CASE WHEN data_year >= 2016 THEN TRUE ELSE FALSE END as has_full_date_tracking,
      CASE WHEN data_year >= 2006 THEN TRUE ELSE FALSE END as has_modern_status_tracking

    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.bills_with_consolidated_intent`
    """
    
    print("🔄 Updating comprehensive_bills_authentic view...")
    try:
        job = client.query(updated_comprehensive_sql)
        job.result()
        print("✅ Successfully updated comprehensive_bills_authentic view")
        return True
    except Exception as e:
        print(f"❌ Failed to update comprehensive view: {e}")
        return False

def create_backward_compatible_unified_view():
    """Create a backward-compatible unified view that uses corrected data."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Create a new unified view that uses corrected data but preserves structure
    unified_corrected_sql = f"""
    CREATE OR REPLACE VIEW `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.all_historical_bills_unified_corrected` AS
    SELECT 
      -- Preserve all existing fields
      *,
      
      -- Add corrected versions as new fields (so dashboards can gradually migrate)
      contraception_corrected,
      emergency_contraception_corrected,
      pregnancy_corrected,
      period_products_corrected,
      incarceration_corrected,
      positive_corrected,
      neutral_corrected,
      restrictive_corrected,
      
      -- Add new consolidated fields
      intent_consolidated,
      intent_tracking_era,
      period_products_tracking_status,
      incarceration_tracking_status
      
    FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.bills_with_consolidated_intent`
    """
    
    print("\n🔄 Creating backward-compatible unified view...")
    try:
        job = client.query(unified_corrected_sql)
        job.result()
        print("✅ Successfully created all_historical_bills_unified_corrected view")
        return True
    except Exception as e:
        print(f"❌ Failed to create unified corrected view: {e}")
        return False

def test_dashboard_compatibility():
    """Test that existing dashboard queries still work with updated views."""
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    dataset_id = "legislative_tracker_historical"
    
    # Test key dashboard queries
    test_queries = [
        # Test 1: Basic field access
        f"""
        SELECT 
          data_year,
          COUNT(*) as total_bills,
          SUM(CASE WHEN abortion = TRUE THEN 1 ELSE 0 END) as abortion_bills,
          SUM(CASE WHEN contraception = TRUE THEN 1 ELSE 0 END) as contraception_bills,
          SUM(CASE WHEN period_products = TRUE THEN 1 ELSE 0 END) as period_products_bills
        FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic`
        WHERE data_year IN (2002, 2016, 2019, 2023)
        GROUP BY data_year
        ORDER BY data_year
        """,
        
        # Test 2: Intent summary usage
        f"""
        SELECT 
          intent_summary,
          COUNT(*) as bills
        FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic`
        WHERE data_year = 2023
        GROUP BY intent_summary
        ORDER BY bills DESC
        """,
        
        # Test 3: Policy area count
        f"""
        SELECT 
          policy_area_count,
          COUNT(*) as bills
        FROM `{os.getenv('GCP_PROJECT_ID')}.{dataset_id}.comprehensive_bills_authentic`
        WHERE data_year = 2023
        GROUP BY policy_area_count
        ORDER BY policy_area_count
        """
    ]
    
    print("\n🧪 TESTING DASHBOARD COMPATIBILITY")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: ", end="")
        try:
            results = client.query(query).result()
            row_count = sum(1 for _ in results)
            print(f"✅ PASSED ({row_count} rows)")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🔄 UPDATING COMPREHENSIVE VIEW WITH CORRECTED DATA")
    print("=" * 70)
    print("This preserves your existing dashboard structure while using corrected data.")
    print("=" * 70)
    
    success = True
    
    # Step 1: Update comprehensive view
    if update_comprehensive_view():
        print("✅ Comprehensive view updated")
    else:
        success = False
    
    # Step 2: Create backward-compatible unified view
    if create_backward_compatible_unified_view():
        print("✅ Backward-compatible view created")
    else:
        success = False
    
    # Step 3: Test dashboard compatibility
    if test_dashboard_compatibility():
        print("✅ Dashboard compatibility confirmed")
    else:
        success = False
    
    if success:
        print(f"\n🎉 UPDATE COMPLETE!")
        print(f"Your existing dashboards should continue working with:")
        print(f"- comprehensive_bills_authentic (updated with corrected data)")
        print(f"- all_historical_bills_unified_corrected (new corrected unified view)")
        print(f"\nKey improvements:")
        print(f"- Period products: NULL before 2019 (was FALSE)")
        print(f"- Incarceration: NULL before 2019 (was FALSE)")
        print(f"- Contraception: NULL 2006-2008 (was FALSE)")
        print(f"- Intent fields: NULL before 2006 (was FALSE)")
        print(f"- New consolidated intent_consolidated field")
        print(f"- Tracking status indicators for policy fields")
    else:
        print(f"\n❌ UPDATE FAILED - please check errors above")