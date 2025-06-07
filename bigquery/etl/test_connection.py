#!/usr/bin/env python3
"""Test connections for BigQuery pipeline."""

import subprocess
import sys
from pathlib import Path

# Test mdbtools
try:
    result = subprocess.run(["mdb-tables", "--help"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ mdbtools installed and working")
    else:
        print("✗ mdbtools not working properly")
except FileNotFoundError:
    print("✗ mdbtools not found. Install with:")
    print("  Mac: brew install mdbtools")
    print("  Linux: sudo apt-get install mdbtools")
    print("  This is required for reading .mdb files")

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
    print(
        "✗ google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery"
    )

print()

# Test for .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    print(f"✓ .env file found at {env_path}")
else:
    print(f"⚠ No .env file found. Copy .env.example to .env and configure")

print()

# Test for MDB files
data_path = Path(__file__).parent.parent / "data" / "historical"
if data_path.exists():
    mdb_files = list(data_path.glob("*.mdb")) + list(data_path.glob("*.accdb"))
    if mdb_files:
        print(f"✓ Found {len(mdb_files)} database files:")
        for f in mdb_files[:5]:  # Show first 5
            print(f"  - {f.name}")
    else:
        print(f"⚠ No .mdb files found in {data_path}")
else:
    print(f"⚠ Historical data directory not found: {data_path}")

print("\nSetup check complete!")
