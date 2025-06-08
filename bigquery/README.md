# BigQuery Historical Data Pipeline v2.0

A production-ready pipeline for processing historical legislative data from Access (.mdb) files and creating analytics-ready datasets in BigQuery for Looker Studio integration.

## 🎯 What This Pipeline Does

1. **Extracts** data from historical Access .mdb files using cross-platform tools
2. **Transforms** inconsistent schemas with intelligent field mapping and validation
3. **Loads** standardized data to BigQuery with optimized batch processing
4. **Creates** union tables combining all historical years
5. **Generates** analytics views optimized for Looker Studio dashboards
6. **Monitors** data quality and provides comprehensive execution reporting

## ✨ Key Features

- **Dual Processing Modes**: Simple (fast) and Advanced (full transformations)
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **Cross-Platform**: Works on Mac, Linux, and Windows (with WSL)
- **Scalable**: Handles large datasets with optimized BigQuery loading
- **Flexible**: Configurable field mappings and transformations
- **Observable**: Detailed logging, statistics, and execution reports

## 🏗️ Architecture

```
Historical .mdb Files
      ↓
   mdbtools extraction (with validation)
      ↓
Data Processing Pipeline
   ├─ Simple Mode: Basic cleaning & standardization
   └─ Advanced Mode: Full transformations & enrichment
      ↓
BigQuery Loading (optimized batches)
      ↓
Union Tables (all years combined)
      ↓
Analytics Views (Looker Studio ready)
```

## 📁 Project Structure

```
bigquery/
├── 📂 etl/                          # Pipeline scripts
│   ├── consolidated_pipeline.py     # 🎯 Main pipeline (v2.0)
│   ├── data_transformer.py          # Advanced transformation logic
│   ├── historical_data_pipeline.py  # Legacy full pipeline
│   ├── test_connection.py           # Environment validation
│   └── archived/                    # Previous pipeline versions
├── 📂 schema/
│   └── field_mappings.yaml          # Configuration for field transformations
├── 📂 sql/
│   └── looker_studio_views.sql      # Optimized SQL views
├── 📂 data/
│   ├── historical/                  # 📥 Place .mdb files here
│   ├── staging/                     # Temporary CSV exports
│   ├── execution/                   # Pipeline execution state and metadata
│   └── README.md
├── 📂 logs/                         # Pipeline execution logs
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── pyproject.toml                   # Code formatting configuration
├── .env.example                     # Environment template
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd /path/to/guttmacher-legislative-tracker/bigquery

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install mdbtools (required for .mdb file processing)
brew install mdbtools                # macOS
# sudo apt-get install mdbtools      # Linux/WSL
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Required configuration:

```bash
GCP_PROJECT_ID=your-actual-project-id
BQ_DATASET_ID=legislative_tracker_staging
BQ_LOCATION=US
```

### 3. Validate Setup

```bash
# Test environment and connections
python etl/consolidated_pipeline.py --validate
```

### 4. Add Your Data

```bash
# Copy .mdb files to the data directory
cp /path/to/your/*.mdb data/historical/
```

### 5. Run Pipeline

```bash
# Simple mode (recommended for first run)
python etl/consolidated_pipeline.py

# Advanced mode (with full transformations)
python etl/consolidated_pipeline.py --advanced

# With debug logging
python etl/consolidated_pipeline.py --log-level DEBUG
```

## 📊 Output Tables and Views

After successful execution, your BigQuery dataset will contain:

### 📋 Data Tables

- `consolidated_bills_YYYY` - Individual year bills (2002, 2003, 2004, etc.)
- `consolidated_categories_YYYY` - Individual year policy categories
- `historical_bills_union` - All bills combined across years
- `historical_categories_union` - All categories combined

### 📈 Analytics Views (Looker Studio Ready)

- `v_bills_summary` - Aggregated statistics by year and state
- `v_bills_trends` - Year-over-year trend analysis
- `looker_main_dashboard` - Primary dashboard data source
- `looker_summary_kpis` - Key performance indicators

## 🔧 Configuration Options

### Processing Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `simple` | Basic cleaning and standardization | Quick processing, initial runs |
| `advanced` | Full transformations with field mapping | Production runs, complex data |
| `validate` | Environment check only | Setup verification |

### Command Line Options

```bash
python etl/consolidated_pipeline.py [OPTIONS]

Options:
  --mode {simple,advanced,validate}  Processing mode
  --advanced                         Shortcut for advanced mode
  --validate                         Shortcut for validate mode
  --log-level {DEBUG,INFO,WARNING,ERROR}  Set logging verbosity
  --project-id TEXT                  Override GCP project ID
  --dataset-id TEXT                  Override BigQuery dataset
  --help                             Show help message
```

### Field Mappings (`schema/field_mappings.yaml`)

Customize how historical fields map to current schema:

```yaml
historical_mappings:
  state_legislative_table:
    bill_id: 
      - "ID"
      - "Bill ID"
      - "BillID"
    state:
      - "State"
      - "State Name"
      - "StateName"
    # Add more mappings as needed
```

## 📈 Looker Studio Integration

### Connecting to BigQuery

1. **Data Source**: Choose BigQuery connector
2. **Project**: Select your GCP project
3. **Dataset**: `legislative_tracker_staging` (or your custom dataset)
4. **Table**: Start with `v_bills_summary` for overview dashboards

### Recommended Visualizations

- **📊 Time Series Chart**: Bills introduced by year/month
- **🗺️ Geographic Map**: Bill activity by state
- **📈 Scorecard**: Key metrics (total bills, enactment rate)
- **📋 Table**: Bill details with drill-down capability

### Key Metrics Available

- Total bills by year, state, and status
- Enactment and veto rates
- Intent distribution (Positive/Neutral/Restrictive)
- Processing timelines (introduction to final action)
- Year-over-year growth rates
- State-by-state comparisons

## 🔍 Data Quality and Monitoring

### Built-in Quality Checks

- **Schema Validation**: Ensures required fields are present
- **Date Format Verification**: Handles multiple date formats
- **Duplicate Detection**: Identifies potential duplicate records
- **Completeness Metrics**: Reports missing data percentages

### Monitoring and Logs

- **Real-time Logging**: Detailed progress and error reporting
- **Execution Statistics**: Processing time, row counts, success rates
- **Error Tracking**: Comprehensive error collection and reporting
- **State Persistence**: Saves execution state for debugging

### Log Locations

- **Console Output**: Real-time progress during execution
- **Log Files**: `logs/pipeline.log` for persistent logging
- **Execution State**: `data/execution/pipeline_state_*.json`

## 🛠️ Troubleshooting

### Common Issues

**mdbtools not found**

```bash
# macOS
brew install mdbtools

# Linux/WSL
sudo apt-get install mdbtools
```

**BigQuery authentication errors**

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**Memory issues with large files**

```bash
# Use simple mode for large datasets
python etl/consolidated_pipeline.py --mode simple

# Process files individually if needed
```

**Date parsing warnings**

- Update `schema/field_mappings.yaml` with specific date formats
- Check for inconsistent date formats in historical data
- Review logs for specific parsing failures

### Performance Optimization

- **Large Files**: Use simple mode first, then advanced mode on processed data
- **Network Issues**: Pipeline includes automatic retries for BigQuery operations
- **Memory Constraints**: Processing happens in chunks to manage memory usage

## 🔄 Adding New Historical Files

To process additional .mdb files:

1. **Copy files** to `data/historical/` directory
2. **Ensure filename contains year** (e.g., "2005 legislation.mdb")
3. **Run pipeline** - it will automatically detect and process new files
4. **Union tables** will be updated to include new data

## 📝 Development

### Code Quality

The project includes comprehensive code quality tools:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Format code
black .
isort .

# Check code quality
flake8 .
mypy .
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=etl
```

## 🔒 Security and Best Practices

### Data Protection

- **No Sensitive Data in Git**: .mdb files and .env excluded from version control
- **Local Processing**: All data stays within your Google Cloud environment
- **Encrypted Transit**: All BigQuery operations use HTTPS/TLS
- **Access Control**: Respects your GCP IAM permissions

### What's Committed to Git

✅ **Source code** and pipeline scripts  
✅ **Configuration templates** and documentation  
✅ **Requirements files** for reproducible environments

### What's NOT Committed

❌ **Historical .mdb files** (sensitive data)  
❌ **Environment variables** (.env file)  
❌ **Generated CSV files** (staging data)  
❌ **Virtual environment** (venv directory)  
❌ **Log files** and execution state

## 📞 Support and Contributing

### Getting Help

1. **Check logs** in `logs/` directory for detailed error messages
2. **Validate environment** with `--validate` flag
3. **Review execution state** in `data/execution/` for debugging
4. **Test with simple mode** before using advanced features

### Performance Metrics

Example pipeline execution (3 years, 394 bills):

- **Simple Mode**: ~30 seconds
- **Advanced Mode**: ~2-3 minutes
- **Memory Usage**: < 1GB peak
- **BigQuery Operations**: ~10-15 table operations

### Project Roadmap

- [ ] Support for additional database formats (.accdb, SQLite)
- [ ] Real-time data streaming capabilities
- [ ] Enhanced data visualization templates
- [ ] Automated data quality reporting
- [ ] Integration with additional BI tools

## 📄 License

This project is designed for the Guttmacher Institute's internal use for legislative data analysis and research purposes.