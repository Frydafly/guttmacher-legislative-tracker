# Migration Guide: From Monolithic to Modular Pipeline

## Overview
This guide helps you transition from the monolithic `migrate.py` to the new modular ETL pipeline while maintaining backward compatibility.

## What's New

### Modular Architecture
```
etl/
├── extractors/     # Data source adapters
├── transformers/   # Schema harmonization
├── loaders/        # BigQuery loading
└── pipeline.py     # Orchestration
```

### Key Benefits for Solo Developer
1. **Smaller files** - Each module is 100-200 lines (vs 900+ line monolith)
2. **Claude-friendly** - Claude can understand full context of each module
3. **Incremental adoption** - Mix old and new code during transition
4. **Future-proof** - Easy to add new data sources without breaking existing ones

## Quick Start

### 1. Test with CSV Export (Safest)
```bash
# Export from Airtable manually, then:
python run_pipeline.py --source csv --file data/airtable_export.csv
```

### 2. Run Incremental Update
```bash
# After initial load, run incremental updates:
python run_pipeline.py --config airtable_export --incremental
```

### 3. Keep Using Old Pipeline
```bash
# Old pipeline still works!
python migrate.py  # Historical data
```

## Migration Steps

### Phase 1: Test New Pipeline (Current)
- ✅ Use for new Airtable exports
- ✅ Keep using `migrate.py` for historical data
- ✅ Test incremental updates

### Phase 2: Add Your Data Source
```python
# Create your custom extractor
from etl.extractors.base import DataSourceAdapter

class YourExtractor(DataSourceAdapter):
    def extract(self, since=None):
        # Your extraction logic
        return df
```

### Phase 3: Gradual Migration
- Move field mappings to `config/field_mappings.yaml`
- Reuse existing BigQuery views
- Keep backward compatibility

## Configuration Examples

### Airtable CSV Export
```json
{
  "source": {
    "type": "csv",
    "config": {
      "file_path": "data/bills_export_2025.csv",
      "date_columns": ["Created", "Last Modified"]
    }
  }
}
```

### Future: Airtable Webhook
```json
{
  "source": {
    "type": "airtable_webhook",
    "config": {
      "webhook_path": "data/webhooks/"
    }
  }
}
```

## Common Tasks

### Add New Data Source
1. Create extractor in `etl/extractors/`
2. Register in factory
3. Create config file
4. Run pipeline

### Modify Field Mappings
Edit `field_mappings.yaml`:
```yaml
core_fields:
  your_new_field: ['Variant1', 'Variant2']
```

### Debug Issues
```bash
# Verbose logging
python run_pipeline.py --verbose

# Test connection only
python -c "from etl import Pipeline; p = Pipeline(); p.validate()"
```

## Backward Compatibility

### Keep Using Old Scripts
- `migrate.py` - Still works for historical .mdb files
- `migrate_2024_csv.py` - Still works for specific CSV format
- All existing BigQuery tables/views remain unchanged

### Gradual Transition
```python
# You can use both pipelines
# Old for historical:
python migrate.py

# New for current data:
python run_pipeline.py --config airtable_export
```

## Best Practices

1. **Start Simple**: Use CSV exports first
2. **Test Incrementally**: Run on small datasets
3. **Keep Backups**: Old pipeline remains functional
4. **Document Changes**: Update configs as you go

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the right directory
cd bigquery
python run_pipeline.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### BigQuery Permissions
```bash
gcloud auth application-default login
```

## Next Steps

1. **Today**: Test with a recent Airtable export
2. **This Week**: Set up incremental updates
3. **Next Month**: Add custom data source if needed
4. **Future**: Automate with GitHub Actions

## Questions?

The modular design makes it easy to:
- Ask Claude about specific modules
- Debug individual components
- Add features incrementally

Remember: The old pipeline still works! This is about making your future work easier, not breaking what works today.