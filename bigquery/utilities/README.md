# Utilities Directory

This directory contains essential helper scripts for the migration and maintenance process.

## 🚀 **Active Utilities** (10 scripts)

### **Ongoing Operations**
- **`add_year.py`** - Add new year data to existing dataset (for 2025+ data)
- **`validate_views.py`** - Validate that BigQuery views are working properly
- **`verify_migration.py`** - Pre-migration verification of logic and setup

### **Analysis & Tracking**
- **`analyze_raw_data_availability.py`** - Analyze field tracking evolution across years
- **`create_raw_data_tracking_view.py`** - Create field tracking status views
- **`check_current_state.py`** - Check overall dataset health and deliverables
- **`check_null_handling.py`** - Compare NULL patterns between views

### **Data Access Support**
- **`check_comprehensive_table.py`** - Guide for Google Sheets export recommendations
- **`list_fields.py`** - Quick reference for available fields

### **Utilities Cleaned Up** ✅
- **Deleted 12 obsolete scripts** (one-time fixes, duplicates)
- **Consolidated 4 duplicate scripts** into existing utilities
- **Updated 3 scripts** with current view names and project references

## 📝 Usage Notes

### Most scripts require:
```bash
# Setup environment
source venv/bin/activate
pip install -r requirements.txt

# Run utility
python utilities/script_name.py
```

### Common Dependencies:
- `google-cloud-bigquery`
- `python-dotenv`
- `pandas`
- `pyyaml`

## ⚠️ Important

These are **one-time utilities** and development scripts. For regular use:
- **Main migration**: Use `migrate.py` (in parent directory)
- **Analysis**: Use BigQuery views directly
- **Documentation**: Refer to main README and guides

Most of these scripts were used during the migration development process and are kept for reference.