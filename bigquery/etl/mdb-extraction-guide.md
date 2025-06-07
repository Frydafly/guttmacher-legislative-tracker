# Extracting Data from Access (.mdb) Files

## Option 1: Python Approach (Recommended)

```python
import pandas as pd
import pyodbc

# Connect to .mdb file
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=path/to/your/file.mdb;'
)
conn = pyodbc.connect(conn_str)

# List all tables
cursor = conn.cursor()
for table_info in cursor.tables(tableType='TABLE'):
    print(table_info.table_name)

# Extract specific table to DataFrame
df = pd.read_sql('SELECT * FROM YourTableName', conn)

# Export to CSV for BigQuery
df.to_csv('output.csv', index=False)
```

## Option 2: MDB Tools (Mac/Linux)

```bash
# Install mdb-tools
brew install mdb-tools  # Mac
apt-get install mdb-tools  # Linux

# List tables
mdb-tables your_file.mdb

# Export table to CSV
mdb-export your_file.mdb "TableName" > table_name.csv

# Export all tables
for table in $(mdb-tables -1 your_file.mdb); do
    mdb-export your_file.mdb "$table" > "${table}.csv"
done
```

## Option 3: Direct Access Export

1. Open .mdb file in Microsoft Access
2. Select table → External Data → Export → Text File
3. Choose CSV format
4. Repeat for each table

## BigQuery Loading

Once you have CSV files:

```bash
# Using bq command line
bq load --source_format=CSV \
  --autodetect \
  your_dataset.table_name \
  table_name.csv

# Or use Python
from google.cloud import bigquery

client = bigquery.Client()
table_id = "your-project.your_dataset.table_name"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
)

with open("table_name.csv", "rb") as source_file:
    job = client.load_table_from_file(
        source_file, table_id, job_config=job_config
    )