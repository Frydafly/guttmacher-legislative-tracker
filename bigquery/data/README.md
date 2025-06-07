# Data Directory

Place your .mdb files here. They will be ignored by git for security.

## Directory Structure

```
data/
├── historical/          # Historical .mdb files from Access
│   └── *.mdb           # Place your .mdb files here
├── staging/            # Temporary CSV exports (auto-generated)
└── processed/          # Tracking which files have been loaded
```

## Usage

1. Copy your .mdb files to the `historical/` subdirectory
2. Update the extraction script with the correct paths:
   ```python
   MDB_PATH = "bigquery/data/historical/your_file.mdb"
   ```
3. Run the extraction script from the project root