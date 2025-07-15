# Documentation Index

Complete guide to all documentation in the BigQuery migration project.

## 📚 Main Documentation

### **🚀 Getting Started**
1. **[README.md](README.md)** - **START HERE** - Main project overview and quick start
2. **[BIGQUERY_USER_GUIDE.md](BIGQUERY_USER_GUIDE.md)** - Non-technical user guide for accessing data

### **📊 Data Reference**
3. **[TRACKING_STATUS_VIEWS_GUIDE.md](TRACKING_STATUS_VIEWS_GUIDE.md)** - Field availability and tracking patterns
4. **[TEAM_MEETING_REPORT_20250711.md](TEAM_MEETING_REPORT_20250711.md)** - Official migration report and status

### **🔧 Technical Reference**
5. **[MIGRATION_FIXES_SUMMARY.md](MIGRATION_FIXES_SUMMARY.md)** - NULL/FALSE pattern fixes and improvements

## 📁 Directory Documentation

### **Subdirectories**
- **[utilities/README.md](utilities/README.md)** - Helper scripts and one-off utilities
- **[logs/README.md](logs/README.md)** - Historical logs and analysis files
- **[sql/README_ANALYTICS.md](sql/README_ANALYTICS.md)** - SQL analysis scripts
- **[docs/looker-studio-quickstart.md](docs/looker-studio-quickstart.md)** - Looker Studio integration

## 🎯 Quick Navigation

### **I want to...**

#### **Access and explore the data**
→ Start with **[README.md](README.md)** then **[BIGQUERY_USER_GUIDE.md](BIGQUERY_USER_GUIDE.md)**

#### **Understand what fields are available by year**
→ **[TRACKING_STATUS_VIEWS_GUIDE.md](TRACKING_STATUS_VIEWS_GUIDE.md)**

#### **Get official migration status and methodology**
→ **[TEAM_MEETING_REPORT_20250711.md](TEAM_MEETING_REPORT_20250711.md)**

#### **Understand recent data fixes and improvements**
→ **[MIGRATION_FIXES_SUMMARY.md](MIGRATION_FIXES_SUMMARY.md)**

#### **Run utility scripts or understand migration process**
→ **[utilities/README.md](utilities/README.md)**

#### **Check historical logs or troubleshoot**
→ **[logs/README.md](logs/README.md)**

## 📈 Data Overview

### **Current Status** (as of July 15, 2025)
- **✅ Complete**: 21 years (2002-2023) - 20,221 bills
- **❌ Missing**: 2024 (empty database file)
- **🔧 Enhanced**: NULL/FALSE patterns fixed, consolidated intent field added

### **Key Views to Use**
1. **`comprehensive_bills_authentic`** - Main dashboard view (recommended)
2. **`tracking_completeness_matrix`** - Field availability checker
3. **`all_historical_bills_unified`** - Raw unified data

## 🔄 Document Update History

| Date | Document | Changes |
|------|----------|---------|
| July 15, 2025 | All docs | Consolidation and cleanup |
| July 15, 2025 | README.md | Complete rewrite with current data |
| July 15, 2025 | TEAM_MEETING_REPORT | Updated with 2023 data and fixes |
| July 15, 2025 | New | Created TRACKING_STATUS_VIEWS_GUIDE |
| July 15, 2025 | New | Created MIGRATION_FIXES_SUMMARY |

---

**Last Updated**: July 15, 2025
**Total Documents**: 9 main files + 4 subdirectory READMEs