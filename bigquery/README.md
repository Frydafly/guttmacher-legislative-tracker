# Guttmacher Legislative Tracker - BigQuery Historical Data

Complete migration pipeline for **21 years (2002-2023)** of legislative tracking data with schema harmonization and analytics optimization.

## 🎯 Overview

**Status**: ✅ Migration Complete (21 years, 20,221 bills)
- Successfully migrated historical .mdb/.accdb files to BigQuery
- Harmonized varying database schemas across 21 years
- Created comprehensive analytics views with proper NULL/FALSE patterns
- Built field tracking status system for data quality assessment

## 📊 Data Available

### **Years Migrated**: 2002-2023 (21 years)
- **Total Bills**: 20,221 bills
- **Missing**: 2024 (empty database file)
- **Data Quality**: Full field tracking status documentation

### **Key Views for Analysis**:
1. **`comprehensive_bills_authentic`** - Main dashboard view (recommended)
2. **`all_historical_bills_unified`** - Raw unified data
3. **`tracking_completeness_matrix`** - Field availability by year
4. **`realistic_field_tracking_by_year`** - Tracking evolution analysis

## 🚀 Quick Start

### For Analysts & Researchers
```sql
-- Start with the main view
SELECT * FROM `comprehensive_bills_authentic` 
WHERE data_year = 2023 AND intent_consolidated = 'Positive';

-- Check what fields are available for a specific year
SELECT * FROM `tracking_completeness_matrix` 
WHERE data_year = 2016;
```

### For Developers
```bash
# Setup environment
cd bigquery
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migration (if needed)
python migrate.py
```

## 📁 Project Structure

```
bigquery/
├── 📊 DATA ACCESS
│   ├── README.md                          # This file
│   ├── BIGQUERY_USER_GUIDE.md            # Non-technical user guide
│   └── TRACKING_STATUS_VIEWS_GUIDE.md    # Field tracking reference
│
├── 📈 MIGRATION DOCUMENTATION  
│   ├── TEAM_MEETING_REPORT_20250711.md   # Official migration report
│   └── MIGRATION_FIXES_SUMMARY.md        # NULL/FALSE pattern fixes
│
├── 🔧 MIGRATION SCRIPTS
│   ├── migrate.py                         # Main migration script
│   ├── field_mappings.yaml               # Schema harmonization
│   └── requirements.txt                  # Dependencies
│
├── 📂 DATA
│   ├── data/                             # Historical database files
│   │   ├── 2002-2023.mdb/.accdb         # Source files
│   │   └── 2024.accdb                   # Empty (migration failed)
│   └── venv/                            # Python environment
│
└── 🔍 ANALYSIS & UTILITIES
    ├── sql/                             # SQL analysis scripts
    ├── docs/                            # Additional documentation
    └── [various utility scripts]
```

## 🔍 Understanding the Data

### **Field Tracking Evolution**
The data preserves the story of evolving methodology:

| Era | Years | Key Features |
|-----|-------|-------------|
| **Foundation** | 2002-2005 | Basic bill identification |
| **Revolution** | 2006-2015 | Modern status tracking |
| **Comprehensive** | 2016-2018 | Full date tracking |
| **Modern** | 2019-2023 | Rich summaries + emerging categories |

### **Critical Data Patterns**
- **NULL vs FALSE**: NULL means "not tracked that year", FALSE means "tracked but negative"
- **Contraception Gap**: Not tracked 2006-2008 (shows as NULL)
- **Period Products**: Only tracked 2019+ (NULL before)
- **Incarceration**: Only tracked 2019+ (NULL before)
- **Intent Consolidated**: Single source of truth for bill intent

## 📊 Key Analytics Views

### **`comprehensive_bills_authentic`** ⭐ **RECOMMENDED**
Enhanced view with dashboard helpers, preserves NULL patterns
```sql
SELECT data_year, state_name, region, intent_consolidated, 
       policy_area_count, abortion, contraception, period_products
FROM `comprehensive_bills_authentic` 
WHERE data_year >= 2019;
```

### **`tracking_completeness_matrix`** 
Visual tracking status (✅/⚠️/❌) by year and field
```sql
SELECT data_year, contraception_tracked, period_products_tracked, 
       incarceration_tracked, intent_fields_tracked
FROM `tracking_completeness_matrix` 
ORDER BY data_year;
```

### **`all_historical_bills_unified`**
Raw unified data for custom analysis
```sql
SELECT * FROM `all_historical_bills_unified` 
WHERE state = 'CA' AND data_year BETWEEN 2020 AND 2023;
```

## 🎯 Common Use Cases

### **1. Dashboard Creation**
Use `comprehensive_bills_authentic` - has all enhancements while preserving compatibility

### **2. Historical Trend Analysis**
Check `tracking_completeness_matrix` first to understand data availability

### **3. Policy Category Analysis**
Use corrected NULL patterns - NULL means not tracked, FALSE means tracked but not applicable

### **4. Intent Analysis**
Use `intent_consolidated` field (Positive, Restrictive, Neutral, Mixed, Unclassified)

## ⚠️ Important Notes

### **Data Quality Considerations**
1. **Always check tracking status** before analysis
2. **2024 data is missing** - database file is empty
3. **Field evolution affects comparability** - use tracking views to understand
4. **NULL patterns are preserved** - critical for authentic analysis

### **Migration Status**
- ✅ **Complete**: 2002-2024 (22 years)
- 🔧 **Fixed**: NULL/FALSE patterns corrected
- 📊 **Enhanced**: Consolidated intent field added

## 🔗 Related Documentation

- **[BigQuery User Guide](BIGQUERY_USER_GUIDE.md)** - Non-technical access guide
- **[Tracking Status Guide](TRACKING_STATUS_VIEWS_GUIDE.md)** - Field availability reference
- **[Team Meeting Report](TEAM_MEETING_REPORT_20250711.md)** - Official migration documentation
- **[Migration Fixes Summary](MIGRATION_FIXES_SUMMARY.md)** - NULL/FALSE pattern corrections

## 🆘 Support

### **Common Issues**
- **Can't see intent_consolidated field**: It's column 42 in comprehensive_bills_authentic
- **Unexpected NULL values**: Check tracking_completeness_matrix for field availability

### **Getting Help**
1. Check the tracking status views first
2. Review the team meeting report for methodology details
3. Consult the migration fixes summary for recent changes

---

**Last Updated**: July 15, 2025 (Added 2023 data, fixed NULL patterns, added consolidated intent field)