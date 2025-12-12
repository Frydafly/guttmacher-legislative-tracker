# Guttmacher Legislative Tracker - BigQuery Pipeline

**Complete data pipeline for historical legislative tracking data (2002-2024) with annual update capability.**

## 🎯 What This Repository Does

This pipeline:
1. **Preserves raw historical data** exactly as it was in original Access databases  
2. **Creates harmonized analytical data** with consistent schema across 22+ years
3. **Provides annual update capability** for adding new years of data

### Key Features
- ✅ **22 years of historical data** (2002-2024) in BigQuery
- ✅ **Raw preservation**: Original field names and structures maintained
- ✅ **Analytical consistency**: Harmonized schema for cross-year analysis  
- ✅ **Annual pipeline**: Simple process for adding new years
- ✅ **Configuration-driven**: Easy to adapt for schema changes

## 🚀 Quick Start Guide

### For Analysts & Data Users

**Access the data in BigQuery:**
- **Project**: `guttmacher-legislative-tracker`
- **Main dataset**: `legislative_tracker_historical` (for analysis)
- **Raw dataset**: `legislative_tracker_staging` (for historical preservation)

**Key tables:**
```sql
-- Harmonized data for analysis
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_historical.all_historical_bills_unified`

-- 2011 example for Amy's analysis
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_historical.analysis_2011_intent_breakdown`

-- Raw data (original field names)  
SELECT * FROM `guttmacher-legislative-tracker.legislative_tracker_staging.raw_historical_2011`
```

### For Administrators & Developers

**Adding a new year (e.g., 2025):**

1. **Setup environment** (first time only):
   ```bash
   cd bigquery
   ./setup_migration_env.sh  # Handles authentication & dependencies
   ```

2. **Add new year's database file**:
   ```bash
   # Copy new .accdb/.mdb file to data/ directory
   cp "2025 Legislative Database.accdb" data/
   ```

3. **Configure the year**:
   ```bash
   # Edit yearly_configs/2025.yaml with correct source file name
   vim yearly_configs/2025.yaml
   ```

4. **Run import**:
   ```bash
   # Import both raw (preservation) and harmonized (analysis) versions
   python3 annual/add_year.py --year 2025
   ```

## 📁 Repository Structure

```
bigquery/
├── 🔧 ANNUAL PIPELINE (for new years)
│   ├── annual/
│   │   ├── add_year.py              # Main script for adding new years
│   │   ├── raw_archive.py           # Raw data preservation
│   │   └── harmonized_import.py     # Analytical data import
│   │
│   ├── yearly_configs/              # Configuration for each year
│   │   ├── 2025.yaml               # Template for new years
│   │   └── field_mappings/         # Custom mappings if needed
│   │
│   └── shared/                     # Common utilities
│       ├── field_mappings.yaml     # Standard field harmonization
│       └── bigquery_utils.py       # BigQuery operations
│
├── 📦 HISTORICAL MIGRATION (completed)
│   ├── archive/                    # Archived historical documentation
│   │   ├── README.md              # Archive inventory
│   │   ├── migrate.py             # Original historical migration script
│   │   ├── 2002_2024_Historical_Migration.md
│   │   ├── ARCHITECTURE_PROPOSAL.md
│   │   └── [incident reports]     # Resolved incidents
│   │
│   ├── MIGRATION_SETUP.md          # Setup guide for annual pipeline
│   ├── MIGRATION_GUIDE.md          # Modular pipeline architecture
│   └── setup_migration_env.sh      # Environment setup script
│
├── 📊 DATA & ANALYSIS  
│   ├── data/                       # Historical database files (.mdb/.accdb)
│   ├── sql/                        # Analysis queries and views
│   └── docs/                       # Additional documentation
│
└── ⚙️ SUPPORTING FILES
    ├── field_mappings.yaml         # Field harmonization rules
    ├── requirements.txt            # Python dependencies
    ├── .env                        # Configuration (created by setup)
    └── venv/                       # Python virtual environment
```

## 📊 Data Architecture

### Raw Data Preservation (`legislative_tracker_staging`)
- **Purpose**: Historical archival exactly as databases were
- **Tables**: `raw_historical_YYYY` (e.g., `raw_historical_2011`)
- **Features**: Original field names, no harmonization, metadata preserved

### Harmonized Data (`legislative_tracker_historical`) 
- **Purpose**: Cross-year analysis with consistent schema
- **Tables**: `historical_bills_YYYY` + unified views
- **Features**: Standardized field names, consistent data types, analytical views

## 🔧 Configuration

### Adding a New Year

**1. Create year configuration:**
```yaml
# yearly_configs/2026.yaml
year: 2026
metadata:
  source_file: "2026 Legislative Database.accdb"
  table_name: "Legislative Monitoring"

raw_import:
  enabled: true                    # Always preserve raw data
  
harmonized_import:
  enabled: true                    # Always create analytical version
  field_mapping: "standard"       # Use standard mapping (or "custom_2026")
```

**2. Custom field mapping (if Airtable fields change):**
```yaml
# yearly_configs/field_mappings/custom_2026.yaml
core_fields:
  new_airtable_field:
    - "New Field Name from Airtable"
    - "Alternative Name"
```

### Modifying Field Mappings

Edit `shared/field_mappings.yaml` to add new field mappings:

```yaml
core_fields:
  bill_number:
    - "BillNumber"
    - "BILLNUMBER"
    - "Bill Number"
    - "New Variant"      # Add new variants here

status_fields:
  enacted:
    - "Enacted"
    - "Passed"
    - "New Status Field"  # Add new status variants
```

## 🔍 Understanding the Data

### Field Evolution Across Years
- **2002-2005**: Basic bill tracking
- **2006-2015**: Modern status tracking introduced  
- **2016-2024**: Full date tracking, rich summaries
- **Special cases**: 2019 "WITH ALL THE SUBPOLICIES" has extra fields

### Data Quality Notes
- **Raw data**: Preserves exact original structure (including problematic field names)
- **Harmonized data**: Consistent schema but may lose some original nuances
- **Missing years**: Some early years (2002-2007) may have limited raw data due to different table structures

## 🆘 Troubleshooting

### Common Issues

**"Permission denied" errors:**
```bash
# Run the setup script to fix authentication
./setup_migration_env.sh
```

**"Table not found" errors:**
```bash
# Check if data exists
bq ls legislative_tracker_historical
bq ls legislative_tracker_staging
```

**Field mapping issues:**
```bash
# Test with verbose logging
python3 annual/add_year.py --year 2025 --verbose
```

### Getting Help

1. **Setup issues**: Run `./setup_migration_env.sh`
2. **Data questions**: Check `sql/` directory for example queries
3. **Configuration**: Look at `yearly_configs/2025.yaml` template
4. **Architecture**: Read archived `archive/ARCHITECTURE_PROPOSAL.md` for historical context

## 📚 Documentation

### Active Documentation (Current Operations)

- **[Migration Setup Guide](MIGRATION_SETUP.md)** - Environment setup and authentication
- **[Migration Guide](MIGRATION_GUIDE.md)** - Guide to modular pipeline architecture
- **[Best Practices](BEST_PRACTICES.md)** - Data handling and pipeline best practices
- **[Quick Reference](QUICK_REFERENCE.md)** - Common commands and queries
- **[Quick Recovery](QUICK_RECOVERY.md)** - Emergency recovery procedures
- **[Safe Testing](SAFE_TESTING.md)** - Testing procedures to avoid production issues
- **[Incidents Log](INCIDENTS.md)** - Record of incidents and resolutions

### Historical Documentation (Archived)

Located in `archive/` directory:

- **[2002-2024 Historical Migration](archive/2002_2024_Historical_Migration.md)** - Completed one-time migration
- **[Architecture Proposal](archive/ARCHITECTURE_PROPOSAL.md)** - Original technical design decisions
- **[Field Fix Summary](archive/FIELD_FIX_SUMMARY.md)** - Resolved field mapping issues
- **Incident Reports** - Completed dashboard and data quality fixes

See [archive/README.md](archive/README.md) for complete archived documentation inventory.

---

**Last Updated**: December 2025 (Documentation reorganized, historical files archived)