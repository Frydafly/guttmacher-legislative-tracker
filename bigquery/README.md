# BigQuery Historical Data Pipeline

Complete pipeline for processing inconsistent historical legislative data (.mdb files) and creating Looker Studio-ready analytics views.

## 🎯 What This Pipeline Does

1. **Extracts** data from historical Access .mdb files
2. **Transforms** inconsistent schemas to match current Airtable structure
3. **Loads** standardized data to BigQuery staging tables
4. **Unions** all historical years into a single dataset
5. **Creates** optimized analytics views for Looker Studio

## 🏗️ Architecture

```
Historical .mdb Files
      ↓
   mdbtools extraction
      ↓
Data Transformation Pipeline
   (schema mapping, type casting, standardization)
      ↓
BigQuery Staging Tables
   (one per year per table type)
      ↓
Union Table
   (all years combined)
      ↓
Analytics Views
   (Looker Studio optimized)
```

## 📁 Directory Structure

```
bigquery/
├── schema/
│   └── field_mappings.yaml         # Configuration for field mappings and transformations
├── etl/
│   ├── data_transformer.py         # Core transformation logic
│   ├── historical_data_pipeline.py # Complete pipeline orchestrator
│   ├── mdb_to_bigquery_pipeline.py # Alternative pipeline (mdbtools)
│   ├── extract_mdb_to_bigquery.py  # Alternative pipeline (pyodbc)
│   ├── explore_mdb_with_mdbtools.py # MDB exploration utility
│   └── test_connection.py          # Setup verification
├── sql/
│   └── looker_studio_views.sql     # Optimized views for Looker Studio
├── data/
│   ├── historical/                 # Place your .mdb files here
│   ├── staging/                    # Temporary CSV exports
│   └── processed/                  # Processing logs and state
├── requirements.txt                # Python dependencies
├── setup.md                       # Installation guide
└── .env                           # Configuration (update with your project ID)
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# From the bigquery directory
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt

# Install mdbtools (Mac/Linux)
brew install mdbtools  # Mac
# sudo apt-get install mdbtools  # Linux
```

### 2. Configure Project

```bash
# Copy environment template and configure
cp .env.example .env

# Edit .env file and update:
# GCP_PROJECT_ID=your-actual-project-id
```

**Important**: Never commit the `.env` file to git. It contains sensitive configuration and is excluded via `.gitignore`.

### 3. Add Your Data

```bash
# Copy your .mdb files to the historical directory
cp /path/to/your/*.mdb data/historical/
```

### 4. Test Setup

```bash
python etl/test_connection.py
```

### 5. Run Pipeline

```bash
# Complete pipeline: extract, transform, load, union, create views
python etl/historical_data_pipeline.py
```

## 📊 Output Tables and Views

After running the pipeline, you'll have:

### Staging Tables
- `staging_historical_bills_2002`
- `staging_historical_bills_2003`
- `staging_historical_bills_2004`
- etc.

### Union Table
- `historical_bills_union` - All years combined

### Analytics Views (Looker Studio Ready)
- `analytics_bills_view` - Main view matching Airtable structure
- `looker_main_dashboard` - Primary dashboard data source
- `looker_summary_kpis` - High-level KPIs and metrics
- `looker_time_series` - Time-based trending analysis
- `looker_geographic_analysis` - State-by-state analysis
- `looker_bill_details` - Detailed bill information
- `looker_data_quality` - Data quality monitoring

## 🔧 Configuration

### Field Mappings (`schema/field_mappings.yaml`)

Controls how historical field names map to current Airtable structure:

```yaml
historical_mappings:
  state_legislative_table:
    bill_id: 
      - "ID"
      - "id"
      - "Bill ID"
    state:
      - "State"
      - "state"
      - "State Name"
    # ... more mappings
```

### Data Transformations

The pipeline handles:
- **Column name mapping** (historical → current schema)
- **Date parsing** (multiple formats)
- **State standardization** (full names → abbreviations)
- **Bill type normalization** 
- **Status categorization**
- **Intent inference** (from bill text)
- **Data quality validation**

## 📈 Looker Studio Integration

### Connecting to BigQuery

1. In Looker Studio, choose "BigQuery" as data source
2. Select your project and dataset
3. Use `looker_main_dashboard` as primary table
4. Join with other views as needed

### Recommended Charts

- **Time Series**: Bills introduced by month/year
- **Geographic**: State map with bill counts
- **KPIs**: Enactment rates, intent distribution
- **Drill-down**: Bill details table

### Key Metrics Available

- Total bills by year/state
- Enactment rates
- Intent distribution (Positive/Restrictive/Neutral)
- Processing times (days to enactment/veto)
- Legislative activity levels
- Year-over-year trends

## 🔍 Data Quality

The pipeline includes comprehensive data quality checks:

- **Required field validation**
- **Date format verification**
- **State code standardization**
- **Duplicate detection**
- **Completeness metrics**

View data quality reports in `looker_data_quality` table.

## 🛠️ Troubleshooting

### Common Issues

**mdbtools not found**
```bash
brew install mdbtools  # Mac
apt-get install mdbtools  # Linux
```

**BigQuery authentication errors**
```bash
gcloud auth application-default login
```

**Date parsing issues**
- Check `field_mappings.yaml` for date formats
- Historical data may have inconsistent date formats

**Missing fields in output**
- Update `field_mappings.yaml` with your specific column names
- Check logs for unmapped columns

### Logs and Monitoring

All operations are logged with detailed information:
- Field mapping results
- Data quality issues
- Transformation statistics
- Load success/failure rates

## 🔄 Adding New Historical Files

To add more .mdb files:

1. Copy files to `data/historical/`
2. Ensure filename contains year (e.g., "2005 legislation.mdb")
3. Run pipeline again - it will process new files automatically

## 📝 Customization

### Adding New Field Mappings

Edit `schema/field_mappings.yaml`:

```yaml
historical_mappings:
  state_legislative_table:
    your_new_field:
      - "Historical Column Name 1"
      - "Historical Column Name 2"
```

### Adding Custom Views

Add SQL to `sql/looker_studio_views.sql` or create new files in the `sql/` directory.

## 🔒 Security & Git Best Practices

- **Virtual Environment**: `venv/` is excluded from git via `.gitignore`
- **Sensitive Data**: `.env` file and `.mdb` files are excluded from git
- **Data Processing**: All operations happen within your Google Cloud project
- **No Data Exposure**: Historical data never leaves your environment

### What's Committed to Git
✅ **Source code** and pipeline scripts  
✅ **Configuration templates** (`.env.example`)  
✅ **Documentation** and setup guides  
✅ **Requirements file** for reproducible environments  

### What's NOT Committed to Git
❌ **Virtual environment** (`venv/`)  
❌ **Environment variables** (`.env`)  
❌ **Database files** (`.mdb`, `.accdb`)  
❌ **Generated data** (`.csv`, processed files)  
❌ **Log files** and temporary data

## 📞 Support

- Check logs for detailed error messages
- Verify your .env configuration
- Ensure BigQuery dataset exists
- Test with `test_connection.py` first