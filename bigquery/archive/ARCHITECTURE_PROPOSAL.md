# BigQuery Pipeline Architecture Proposal

## Current Issues with migrate.py

The current `migrate.py` is a **monolithic historical migration script** that:
- ✅ Works great for one-time historical data migration (2002-2024)
- ❌ Is overkill for annual updates (re-processes everything)
- ❌ Mixes historical harmonization with ongoing data needs
- ❌ Doesn't separate raw archival from analytical processing

## Proposed Architecture

### 1. **One-Time Historical Migration** (DONE ✅)
```
migrate.py → Archive and retire after historical migration complete
```

### 2. **Annual Data Pipeline** (NEW)
```
add_year.py → Simple script for new year addition
├── Raw import (preserve original structure)
└── Harmonized import (current analytical schema)
```

### 3. **Configuration-Driven Approach**
```yaml
# yearly_configs/2025.yaml
year: 2025
source_file: "2025 Legislative Database.accdb"
table_name: "Legislative Monitoring"
field_mapping: "standard"  # vs "custom" for edge cases
raw_archive: true
harmonized_import: true
```

## Detailed Design

### Raw Archival Strategy
**Purpose**: Preserve each year's database exactly as it was
```python
# raw_archive.py
def archive_year_raw(year: int, source_file: Path):
    """Import year's data with NO field modifications"""
    table_name = f"raw_historical_{year}"
    # Direct mdb-export → BigQuery with original field names
    # No harmonization, no field mapping
    # Pure historical preservation
```

### Harmonized Import Strategy  
**Purpose**: Add new year to analytical dataset
```python
# harmonized_import.py
def import_year_harmonized(year: int, config: YearConfig):
    """Import year's data with field harmonization for analysis"""
    # Use field_mappings.yaml for standardization
    # Apply current analytical schema
    # Update unified views automatically
```

### Configuration Structure
```
yearly_configs/
├── 2024.yaml
├── 2025.yaml
├── 2026.yaml
└── field_mappings/
    ├── standard.yaml        # Current mapping (most years)
    ├── early_2000s.yaml    # Special mapping for 2002-2005
    └── custom_2019.yaml    # Special handling for "WITH ALL THE SUBPOLICIES"
```

## File Organization

### Archive Historical Migration
```
archive/
└── migrate.py              # Move here after historical migration complete
└── historical_migration.log
```

### New Annual Pipeline
```
annual/
├── add_year.py             # Main script for new year
├── raw_archive.py          # Raw import functionality
├── harmonized_import.py    # Analytical import
└── yearly_configs/         # Configuration per year
```

### Shared Resources
```
shared/
├── field_mappings.yaml     # Current standard mapping
├── bigquery_utils.py       # Common BQ operations
└── mdb_utils.py           # Common mdb operations
```

## Yearly Process (Future)

### Step 1: Raw Archive (Always)
```bash
python annual/raw_archive.py --year 2025 --source "data/2025 Legislative Database.accdb"
```
**Result**: `raw_historical_2025` table with original field names

### Step 2: Harmonized Import (Always)  
```bash
python annual/harmonized_import.py --year 2025 --config yearly_configs/2025.yaml
```
**Result**: `historical_bills_2025` table with standardized schema

### Step 3: Update Analytics (Automatic)
- Refresh unified views
- Update materialized tables
- Regenerate Looker Studio tables

## Benefits

### ✅ **Separation of Concerns**
- Raw archival = Historical preservation
- Harmonized import = Analytical consistency
- One-time migration = Different from ongoing updates

### ✅ **Configuration-Driven**
- Each year has its own config file
- Field mappings can evolve without code changes
- Special cases handled via config, not code

### ✅ **Maintainable**
- Small, focused scripts vs monolithic migration
- Easy to debug individual components
- Clear separation of historical vs ongoing

### ✅ **Flexible**
- Can re-import just harmonized data if schema changes
- Raw data always preserved unchanged
- Can handle schema evolution gracefully

## Migration Plan

### Phase 1: Archive Current System ✅ DONE
- `migrate.py` successfully loaded all historical data
- Ready to archive this approach

### Phase 2: Build Annual Pipeline
```bash
# Create new structure
mkdir -p annual yearly_configs shared archive
mv migrate.py archive/

# Build new components
python create_annual_pipeline.py
```

### Phase 3: Test with 2025 Data
```bash
# When 2025 data arrives, test new pipeline
python annual/add_year.py --year 2025
```

## Example: 2025 Configuration

```yaml
# yearly_configs/2025.yaml
year: 2025
metadata:
  source_file: "2025 Legislative Database.accdb"
  table_name: "Legislative Monitoring"
  created_date: "2025-12-31"
  notes: "Standard structure expected"

raw_import:
  enabled: true
  table_name: "raw_historical_2025"
  preserve_all_fields: true

harmonized_import:
  enabled: true
  table_name: "historical_bills_2025"
  field_mapping: "standard"
  apply_transformations: true
  
post_import:
  update_unified_view: true
  refresh_materialized_table: true
  update_looker_table: true
```

This approach gives you both **historical preservation** and **analytical consistency** while keeping the pipeline maintainable for future years.