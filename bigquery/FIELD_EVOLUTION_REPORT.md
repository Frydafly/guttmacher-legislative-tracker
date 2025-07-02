# Field Evolution Report: Guttmacher Legislative Tracker BigQuery Pipeline

## Executive Summary

This report documents the evolution of data fields in the Guttmacher Legislative Tracker database from 2002-2024, the challenges encountered during historical data migration, and the solutions implemented to create a unified BigQuery dataset for analytics.

**Key Findings:**
- **Complete Coverage**: 23 consecutive years of data (2002-2024) with no gaps
- **Field Evolution**: Significant changes in field names, categories, and data structure over time  
- **Schema Harmonization**: Successfully unified 200+ field variations into a standardized schema
- **NULL Handling**: Implemented proper distinction between "not tracked" (NULL) vs "explicitly false" (FALSE)

## Historical Data Coverage

### Database Files Available
- **2002-2019**: Microsoft Access .mdb format
- **2020-2024**: Microsoft Access .accdb format  
- **Total**: 23 consecutive years, no gaps in coverage

### Data Volume by Year
| Year | Bills | Notable Changes |
|------|-------|----------------|
| 2005 | 1,956 | Early tracking system |
| 2006 | 8,414 | Volume increase, table rename |
| 2007 | 11,543 | Peak volume period |
| 2012 | 6,240 | Standardized structure |
| 2015 | 3,716 | Modern schema introduction |
| 2020 | 1,558 | COVID impact |
| 2021 | 6,670 | Post-COVID recovery |
| 2022 | 9,170 | High activity year |

## Field Evolution Timeline

### Phase 1: Early Tracking (2002-2008)
**Table Names**: "2005 State Legislative Table" → "2006 Monitoring Table"

**Core Fields Established**:
- Basic bill tracking (ID, state, title, status)
- Early policy categories (5-7 categories)
- Simple date tracking

**Policy Categories**:
- Abortion
- Appropriations  
- Insurance
- Teen Issues (later became "Minors")
- Family Planning/MCH (later became "Contraception")

### Phase 2: Expansion Period (2009-2014)
**Table Names**: Standardized to "Legislative Monitoring Table"

**New Categories Added**:
- Emergency Contraception (EC)
- Refusal (conscience clauses)
- Fetal Personhood/Fetal Issues
- Enhanced status tracking

**Field Name Variations**:
- "EC" vs "Emergency Contraception"
- "Teen Issues" vs "Minors" 
- "Fetal Personhood" vs "Fetal Issues"

### Phase 3: Modern Structure (2015-2019)
**Table Names**: Simplified to "Legislative Monitoring"

**Major Additions**:
- Bill type classification (Legislation, Resolution, Constitutional Amendment, Ballot Initiative)
- Intent classification (Positive, Neutral, Restrictive)
- Enhanced metadata tracking
- Standardized naming conventions

### Phase 4: Contemporary Tracking (2020-2024)
**Table Names**: "Copy of Legislative Monitoring" 

**Recent Additions**:
- Court Case category (2019+)
- Period Products category
- STI/Sexual Health categories
- Incarceration-related reproductive health
- Fetal Tissue research

## Schema Harmonization Challenges

### Challenge 1: Inconsistent Field Names
**Problem**: Same concept, different names across years
- "Teen Issues" (2005) → "Minors" (2010+)
- "Family Planning/MCH" (2005) → "Contraception" (2015+)
- "EC" (2009) → "Emergency Contraception" (2015+)

**Solution**: Created comprehensive field mapping in `field_mappings.yaml`
```yaml
policy_categories:
  minors:
    - "Teen Issues"
    - "Minors"
    - "minors"
  contraception:
    - "Family Planning/MCH"  
    - "Contraception"
    - "contraception"
```

### Challenge 2: Boolean Field Defaults
**Problem**: How to handle missing categories in early years?
- Should missing "Period Products" in 2005 be FALSE or NULL?
- FALSE implies "explicitly not related to period products"
- NULL implies "period products category wasn't tracked yet"

**Original Approach**: All Boolean fields defaulted to FALSE

**Improved Solution**: Distinguished field types:
- **Status Fields**: Default to FALSE (introduced, enacted, vetoed, etc.)
- **Category Fields**: Default to NULL when not tracked (period_products, stis, etc.)
- **Intent Fields**: Default to NULL when not tracked (positive, neutral, restrictive)
- **Bill Type Fields**: Default to NULL when not tracked (court_case, etc.)

### Challenge 3: Date Format Variations
**Problem**: Multiple date formats across years
- "MM/DD/YYYY" in early years
- "YYYY-MM-DD" in later years  
- Text dates like "January 15, 2020"
- Null/empty dates

**Solution**: Robust date parsing with fallback handling
```python
def parse_date_flexible(date_str):
    formats = ['%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y', '%m-%d-%Y']
    # Try each format, return None if unparseable
```

### Challenge 4: Database Structure Evolution
**Problem**: Table names and structures changed significantly
- 2005: "2005 State Legislative Table"
- 2006: "2006 Monitoring Table" 
- 2008: "Legislative Monitoring Table"
- 2015: "Legislative Monitoring"
- 2022: "Copy of Legislative Monitoring"

**Solution**: Dynamic table detection and mapping
```python
def find_main_table(db_file):
    # Search for tables matching known patterns
    patterns = ['Legislative Monitoring', 'State Legislative', 'Monitoring Table']
```

## Data Quality Solutions

### Missing Data Handling
**Status**: ✅ Implemented
- NULL for categories not tracked in early years
- FALSE for status fields when not explicitly set
- Proper distinction between "not applicable" and "not tracked"

### Field Mapping Verification  
**Status**: ✅ Implemented
- Comprehensive mapping of 200+ field variations
- Reverse mapping validation
- Statistics tracking for unmapped fields

### Date Standardization
**Status**: ✅ Implemented  
- All dates converted to YYYY-MM-DD format
- Invalid dates handled gracefully (set to NULL)
- Metadata preserved about original format

### Schema Validation
**Status**: ✅ Implemented
- BigQuery type validation
- String length limits enforced
- Boolean field validation

## BigQuery Implementation

### Table Structure
```sql
-- Individual year tables
historical_bills_2002, historical_bills_2003, ..., historical_bills_2024

-- Unified view
comprehensive_bills_view (combines all years)

-- Looker Studio table  
looker_comprehensive_bills (optimized for dashboard use)
```

### Key Features
- **Partitioned by year** for query performance
- **Indexed on common fields** (state, bill_id, policy categories)
- **NULL-safe aggregations** for proper analytics
- **Metadata tracking** (migration_date, data_source, data_year)

## Impact on Analytics

### Before Migration
- 23 separate Access databases
- Inconsistent field names
- Manual data consolidation required
- Limited cross-year analysis

### After Migration  
- Single unified BigQuery dataset
- Standardized schema across all years
- Looker Studio dashboards possible
- Advanced analytics and trend analysis enabled

### Analytical Considerations
1. **NULL vs FALSE**: Queries must account for NULL values in category fields
2. **Field Evolution**: Some categories only meaningful for certain year ranges
3. **Data Quality**: Early years may have less complete data
4. **Volume Changes**: Significant variation in bill volume across years

## Future Maintenance

### Adding New Years
Use the new `add_year.py` pipeline:
```bash
python add_year.py 2025                # Add 2025 data  
python add_year.py 2025 --test         # Test first
python add_year.py 2024 --update       # Update existing year
```

### Schema Updates
1. Update `field_mappings.yaml` for new field mappings
2. Modify Boolean field categorization if needed
3. Test with sample data before full migration
4. Update Looker views as needed

### Monitoring
- Regular validation of data quality
- Monitoring for new field variations
- Performance optimization as dataset grows

## Technical Specifications

### Dependencies
- Python 3.8+
- Google Cloud BigQuery
- mdbtools (for Access database reading)
- pandas, PyYAML, python-dotenv

### Performance
- Migration time: ~2-3 hours for full dataset
- Single year addition: ~10-15 minutes
- Query performance: Optimized for year-based partitioning

### Security
- No sensitive data in repository
- Environment variables for credentials
- Audit logging for all changes

## Conclusion

The historical data migration successfully unified 23 years of legislative tracking data into a coherent BigQuery dataset. Key achievements:

1. **Complete Coverage**: No data gaps from 2002-2024
2. **Schema Consistency**: Unified field names and types
3. **Proper NULL Handling**: Distinction between missing and false values
4. **Future-Proof**: Pipeline ready for ongoing year additions
5. **Analytics Ready**: Optimized for Looker Studio and advanced analytics

The solution balances historical fidelity with analytical utility, preserving the evolution of tracking practices while enabling modern data analysis workflows.

---

*Report generated as part of Guttmacher Legislative Tracker BigQuery Migration Project*  
*Last updated: July 2025*