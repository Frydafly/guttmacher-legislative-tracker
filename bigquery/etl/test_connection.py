#!/usr/bin/env python3
"""Test connections for BigQuery pipeline."""

import sys
from pathlib import Path

# Test pyodbc
try:
    import pyodbc
    drivers = pyodbc.drivers()
    print("✓ pyodbc installed successfully")
    print(f"  Available ODBC drivers: {drivers}")
    
    access_drivers = [d for d in drivers if 'Access' in d or 'MDB' in d or 'Microsoft' in d]
    if access_drivers:
        print(f"  Access-compatible drivers found: {access_drivers}")
    else:
        print("  ⚠ No Access drivers found. You may need to:")
        print("    - On Mac: Use mdbtools or install Microsoft ODBC driver")
        print("    - On Windows: Drivers should be pre-installed")
        print("    - On Linux: Install mdbtools")
except ImportError:
    print("✗ pyodbc not installed. Run: pip install pyodbc")
    print("  Note: You may need to install ODBC drivers first (see setup.md)")

print()

# Test pandas
try:
    import pandas as pd
    print(f"✓ pandas installed (version {pd.__version__})")
except ImportError:
    print("✗ pandas not installed. Run: pip install pandas")

print()

# Test Google Cloud
try:
    from google.cloud import bigquery
    print("✓ google-cloud-bigquery installed")
    
    try:
        client = bigquery.Client()
        print(f"✓ Connected to GCP project: {client.project}")
        
        # Try to list datasets
        datasets = list(client.list_datasets())
        print(f"  Found {len(datasets)} datasets")
    except Exception as e:
        print(f"✗ Could not connect to BigQuery: {e}")
        print("  Make sure to run: gcloud auth application-default login")
except ImportError:
    print("✗ google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery")

print()

# Test for .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    print(f"✓ .env file found at {env_path}")
else:
    print(f"⚠ No .env file found. Copy .env.example to .env and configure")

print()

# Test for MDB files
data_path = Path(__file__).parent.parent / 'data' / 'historical'
if data_path.exists():
    mdb_files = list(data_path.glob('*.mdb')) + list(data_path.glob('*.accdb'))
    if mdb_files:
        print(f"✓ Found {len(mdb_files)} database files:")
        for f in mdb_files[:5]:  # Show first 5
            print(f"  - {f.name}")
    else:
        print(f"⚠ No .mdb files found in {data_path}")
else:
    print(f"⚠ Historical data directory not found: {data_path}")

print("\nSetup check complete!")