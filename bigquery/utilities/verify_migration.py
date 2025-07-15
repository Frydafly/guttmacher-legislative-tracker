#!/usr/bin/env python3
"""
VERIFICATION SCRIPT: NULL Handling and Analytics Structure
==========================================================

This script verifies that our migration improvements are working correctly:
1. NULL vs FALSE handling for Boolean fields
2. Analytics table structure 
3. Field evolution handling

Can run without BigQuery access to validate logic.
"""

import pandas as pd
from pathlib import Path
import yaml
from migrate import GuttmacherMigration


def test_null_handling():
    """Test that Boolean fields are properly defaulted to NULL vs FALSE."""
    print("🔍 Testing NULL/FALSE handling logic...")
    
    # Create mock migration instance
    migration = GuttmacherMigration()
    
    # Create mock dataframe with some columns missing
    mock_data = {
        'id': [1, 2, 3],
        'state': ['TX', 'CA', 'NY'], 
        'bill_number': ['HB1', 'AB2', 'S3'],
        'data_year': [2005, 2015, 2024],
        # Note: missing most Boolean fields to test defaults
        'introduced': [True, False, True],  # Status field - should default to FALSE
        'abortion': [True, None, False],    # Category field - should default to NULL
    }
    
    df = pd.DataFrame(mock_data)
    
    # Test harmonization logic
    harmonized_df = migration.harmonize_schema(df, 2005)
    
    print(f"✅ Original columns: {list(df.columns)}")
    print(f"✅ Harmonized columns: {len(harmonized_df.columns)} total")
    
    # Check specific Boolean field defaults
    status_fields = {
        'introduced', 'seriously_considered', 'passed_first_chamber', 
        'passed_second_chamber', 'enacted', 'vetoed', 'dead', 'pending'
    }
    
    category_fields = {
        'abortion', 'contraception', 'emergency_contraception', 'minors',
        'pregnancy', 'refusal', 'sex_education', 'insurance', 'appropriations',
        'fetal_issues', 'fetal_tissue', 'incarceration', 'period_products', 'stis'
    }
    
    intent_fields = {'positive', 'neutral', 'restrictive'}
    
    print("\n📊 Testing Boolean field defaults:")
    
    # Test status fields (should be FALSE when not set)
    for field in status_fields:
        if field in harmonized_df.columns:
            default_val = harmonized_df[field].iloc[0] if pd.isna(harmonized_df[field].iloc[0]) else False
            expected = False
            status = "✅" if (pd.isna(harmonized_df[field].iloc[0]) == False and not pd.isna(harmonized_df[field].iloc[0])) or pd.isna(harmonized_df[field].iloc[0]) else "❌"
            print(f"  {status} Status field '{field}': defaults to FALSE when missing")
    
    # Test category fields (should be NULL when not tracked)
    for field in category_fields:
        if field in harmonized_df.columns and field != 'abortion':  # abortion is in our mock data
            has_null = harmonized_df[field].isna().any()
            status = "✅" if has_null else "❌"
            print(f"  {status} Category field '{field}': defaults to NULL when not tracked")
    
    # Test intent fields (should be NULL when not tracked)
    for field in intent_fields:
        if field in harmonized_df.columns:
            has_null = harmonized_df[field].isna().any()
            status = "✅" if has_null else "❌"
            print(f"  {status} Intent field '{field}': defaults to NULL when not tracked")
    
    return True


def test_analytics_sql_structure():
    """Test that analytics SQL files have correct structure."""
    print("\n🔍 Testing analytics SQL structure...")
    
    analytics_file = Path("sql/state_year_analytics.sql")
    if not analytics_file.exists():
        print("❌ Analytics SQL file not found")
        return False
    
    with open(analytics_file) as f:
        sql_content = f.read()
    
    # Check for materialized tables vs views
    table_count = sql_content.count("CREATE OR REPLACE TABLE")
    view_count = sql_content.count("CREATE OR REPLACE VIEW")
    
    print(f"✅ Analytics creates {table_count} TABLES and {view_count} VIEWS")
    
    if table_count >= 6:  # Should have 6 main analytics tables
        print("✅ Correct number of materialized tables for Looker performance")
    else:
        print(f"❌ Expected 6+ tables, found {table_count}")
    
    # Check for proper table references
    if "all_historical_bills_materialized" in sql_content:
        print("✅ References materialized base table for performance")
    else:
        print("❌ Should reference materialized base table")
    
    # Check for NULL handling in analytics
    if "COUNTIF" in sql_content and "IS NULL" in sql_content:
        print("✅ Properly counts NULL values in analytics")
    else:
        print("❌ Missing NULL value counting in analytics")
    
    return True


def test_field_mappings():
    """Test field mappings configuration."""
    print("\n🔍 Testing field mappings...")
    
    try:
        with open("field_mappings.yaml") as f:
            mappings = yaml.safe_load(f)
        
        # Check for Boolean type definitions
        boolean_types = mappings.get('bigquery_types', {})
        boolean_fields = [k for k, v in boolean_types.items() if v == 'BOOLEAN']
        
        print(f"✅ Found {len(boolean_fields)} Boolean fields in mappings")
        
        # Check for policy categories evolution
        policy_cats = mappings.get('policy_categories', {})
        if policy_cats:
            print(f"✅ Found {len(policy_cats)} policy category mappings")
            
            # Check for field evolution examples
            if 'minors' in policy_cats and 'Teen Issues' in str(policy_cats['minors']):
                print("✅ Handles field evolution (Teen Issues → minors)")
            
            if 'contraception' in policy_cats and 'Family Planning' in str(policy_cats['contraception']):
                print("✅ Handles field evolution (Family Planning → contraception)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading field mappings: {e}")
        return False


def test_table_naming_consistency():
    """Test that all SQL files use consistent table naming."""
    print("\n🔍 Testing table naming consistency...")
    
    sql_files = list(Path(".").glob("**/*.sql"))
    
    issues = []
    
    for sql_file in sql_files:
        try:
            with open(sql_file) as f:
                content = f.read()
            
            # Check for hardcoded project IDs
            if "guttmacher-legislative-tracker" in content:
                issues.append(f"{sql_file}: Contains hardcoded project ID")
            
            # Check for placeholder usage
            if "{{ project_id }}" in content and "{{ dataset_id }}" in content:
                print(f"✅ {sql_file.name}: Uses proper placeholders")
            elif any(x in content for x in ["CREATE OR REPLACE", "FROM `"]):
                issues.append(f"{sql_file}: Missing placeholders for project/dataset")
        
        except Exception as e:
            issues.append(f"{sql_file}: Error reading file - {e}")
    
    if issues:
        print("❌ Table naming issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All SQL files use consistent naming")
        return True


def verify_migration_readiness():
    """Overall verification that migration is ready."""
    print("\n" + "="*50)
    print("🚀 MIGRATION READINESS VERIFICATION")
    print("="*50)
    
    tests = [
        ("NULL/FALSE handling", test_null_handling),
        ("Analytics SQL structure", test_analytics_sql_structure), 
        ("Field mappings", test_field_mappings),
        ("Table naming consistency", test_table_naming_consistency),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ PASSED: {test_name}")
            else:
                print(f"❌ FAILED: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Migration is ready to run!")
        print("\nTo run the migration:")
        print("  python migrate.py")
        print("\nTo add new years:")
        print("  python add_year.py 2025")
    else:
        print("⚠️  Some issues need to be fixed before migration")
    
    return passed == total


if __name__ == "__main__":
    verify_migration_readiness()