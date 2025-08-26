# Best Practices for Annual-Use BigQuery Pipeline

**Project Type**: Personal, annual-use data pipeline  
**Frequency**: Used once per year to add new legislative data  
**User**: Single developer/analyst (you)

## 🏗️ Architecture Principles

### Separation of Concerns
- **Historical Migration** (`archive/migrate.py`) - One-time script, already completed
- **Annual Pipeline** (`annual/`) - Lightweight, config-driven yearly imports
- **Raw Preservation** (`staging dataset`) - Exact historical archival
- **Analytical Data** (`historical dataset`) - Harmonized for analysis

### Configuration-Driven Design
- Each year has a config file (`yearly_configs/YYYY.yaml`)
- Field mappings centralized in `shared/field_mappings.yaml`
- No hardcoded values in scripts

## 🔧 Robustness for Annual Use

### Environment Consistency
1. **Virtual Environment**: Always use `venv/` to avoid dependency drift
2. **Authentication Script**: `setup_migration_env.sh` handles authentication issues
3. **Requirements Pinning**: `requirements.txt` pins exact versions

### Error Handling
```python
# Good: Explicit error handling with context
try:
    result = process_year(year)
except FileNotFoundError as e:
    logger.error(f"Data file missing: {e}")
    return False
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return False
```

### Validation & Testing
- **Configuration validation**: Check files exist before processing
- **Data quality checks**: Row counts, required fields, null percentages
- **Dry run capability**: Test configs without uploading to BigQuery

## 📅 Annual Workflow Best Practices

### Pre-Season (November/December)
1. **Environment Check**: Run `./setup_migration_env.sh`
2. **Dependency Update**: Consider updating `requirements.txt`
3. **Access Check**: Verify BigQuery permissions still work

### During Season (January/February - New Data Available)
1. **File Preparation**: Place new `.accdb` or `.csv` file in `data/` directory
2. **Configuration**: Copy and modify `yearly_configs/YYYY.yaml`
3. **Validation**: Run with `--verbose` to check field mappings
4. **Import**: Run both raw and harmonized imports
5. **Quality Check**: Verify data in BigQuery looks correct

### Post-Season (March)
1. **Documentation**: Update any field mapping changes
2. **Cleanup**: Archive old log files if needed
3. **Backup**: Ensure data is properly backed up in BigQuery

## 🛡️ Defensive Programming

### File Handling
```python
# Check file exists before processing
if not source_file.exists():
    logger.error(f"Source file not found: {source_file}")
    return False

# Validate file format
if not source_file.suffix in ['.mdb', '.accdb']:
    logger.error(f"Invalid file format: {source_file.suffix}")
    return False
```

### Database Operations
```python
# Always check table existence before operations
if not table_exists(table_name):
    logger.info(f"Creating new table: {table_name}")
else:
    logger.warning(f"Table exists, will replace: {table_name}")

# Validate schema before upload
if not validate_schema(dataframe, expected_fields):
    logger.error("Schema validation failed")
    return False
```

### Configuration Management
- **Default values**: Always provide sensible defaults
- **Validation**: Check all required config fields exist
- **Documentation**: Each config file has examples and comments

## 📊 Monitoring & Logging

### Comprehensive Logging
- **Progress tracking**: Log each major step
- **Error context**: Include relevant details in error messages
- **Metrics**: Log row counts, processing time, data quality stats

### Quality Metrics
```yaml
quality_checks:
  min_row_count: 500              # Catch incomplete extracts
  required_fields: ["state", "bill_number"]  # Essential fields
  max_null_percentage: 0.1        # Data completeness threshold
```

## 🔄 Maintenance Strategy

### Code Maintenance (Minimal, but Important)
- **No over-engineering**: Keep it simple since it's used once/year
- **Clear documentation**: You'll forget details between uses
- **Error messages**: Make them actionable for future-you

### Data Architecture Maintenance
- **Schema evolution**: Field mappings handle new/changed fields
- **Historical consistency**: Raw data preserves exact original structure
- **Analytical evolution**: Harmonized views can evolve without losing history

### Dependency Management
```bash
# Annual dependency check (optional)
pip list --outdated
pip install --upgrade google-cloud-bigquery pandas pyyaml

# Update requirements.txt if needed
pip freeze > requirements.txt
```

## 🚨 Common Failure Points & Solutions

### Authentication Issues
- **Problem**: "User does not have bigquery.jobs.create permission"  
- **Solution**: Run `./setup_migration_env.sh` to fix ADC quota project

### File Format Changes
- **Problem**: Table names change in new Access databases
- **Solution**: Update `yearly_configs/YYYY.yaml` with correct table name

### Schema Evolution  
- **Problem**: New fields in yearly data
- **Solution**: Add to `shared/field_mappings.yaml` or create custom mapping

### Missing Dependencies
- **Problem**: Python packages not found
- **Solution**: Always `source venv/bin/activate` before running scripts

## ✅ Success Criteria

A successful annual run should:
1. **Environment setup** completes without errors
2. **Raw import** preserves all original fields and data
3. **Harmonized import** maps to consistent analytical schema
4. **Quality checks** pass (row counts, required fields, etc.)
5. **BigQuery tables** are accessible and queryable
6. **Documentation** is updated for any new field mappings

## 📝 Annual Checklist

### Before Running
- [ ] `./setup_migration_env.sh` completes successfully
- [ ] New data file exists in `data/` directory  
- [ ] Configuration file created/updated in `yearly_configs/`
- [ ] Virtual environment activated

### During Running
- [ ] Raw import completes with expected row count
- [ ] Harmonized import completes with field mapping success
- [ ] Quality checks pass
- [ ] BigQuery tables are queryable

### After Running
- [ ] Spot-check data in BigQuery looks correct
- [ ] Update field mappings if any new fields discovered
- [ ] Commit configuration changes to git
- [ ] Update main documentation if needed

---

**Remember**: This is a once-yearly tool. Prioritize clarity and robustness over performance optimization. Future-you will thank present-you for clear error messages and comprehensive logging.