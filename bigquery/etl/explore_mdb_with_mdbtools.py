#!/usr/bin/env python3
"""
Explore MDB files using mdbtools (Mac/Linux alternative to pyodbc).
First install: brew install mdbtools
"""

import subprocess
from pathlib import Path

import pandas as pd


def list_tables_in_mdb(mdb_path):
    """List all tables in an MDB file using mdbtools."""
    try:
        result = subprocess.run(
            ["mdb-tables", "-1", str(mdb_path)], capture_output=True, text=True
        )
        if result.returncode == 0:
            tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
            return tables
        else:
            print(f"Error: {result.stderr}")
            return []
    except FileNotFoundError:
        print("mdbtools not found. Install with: brew install mdbtools")
        return []


def export_table_to_csv(mdb_path, table_name, output_path):
    """Export a table from MDB to CSV using mdbtools."""
    cmd = ["mdb-export", str(mdb_path), table_name]

    try:
        with open(output_path, "w") as f:
            result = subprocess.run(cmd, stdout=f, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error exporting {table_name}: {e}")
        return False


def get_table_schema(mdb_path, table_name):
    """Get basic schema info for a table."""
    cmd = ["mdb-schema", str(mdb_path), "-T", table_name]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"Error getting schema: {e}")
        return None


def main():
    # Find MDB files
    data_path = Path(__file__).parent.parent / "data" / "historical"
    mdb_files = list(data_path.glob("*.mdb"))

    if not mdb_files:
        print("No .mdb files found")
        return

    print(f"Found {len(mdb_files)} MDB files:\n")

    # Process each MDB file
    for mdb_file in mdb_files:
        print(f"\n{'='*60}")
        print(f"File: {mdb_file.name}")
        print(f"{'='*60}")

        # List tables
        tables = list_tables_in_mdb(mdb_file)
        print(f"\nFound {len(tables)} tables:")

        for i, table in enumerate(tables[:10]):  # Show first 10
            print(f"  {i+1:2d}. {table}")

        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more tables")

        # Sample export of first few tables
        staging_path = Path(__file__).parent.parent / "data" / "staging"
        staging_path.mkdir(exist_ok=True)

        print("\nExporting sample tables to CSV...")
        for table in tables[:3]:  # Export first 3 tables as sample
            output_file = staging_path / f"{mdb_file.stem}_{table}.csv"
            if export_table_to_csv(mdb_file, table, output_file):
                # Check file size
                size = output_file.stat().st_size / 1024  # KB
                print(f"  ✓ Exported {table} ({size:.1f} KB)")

                # Show sample data
                try:
                    df = pd.read_csv(output_file, nrows=5)
                    print(f"    Columns: {', '.join(df.columns[:5])}")
                    print(f"    Rows: {len(pd.read_csv(output_file))}")
                except Exception as e:
                    print(f"    Could not read CSV: {e}")


if __name__ == "__main__":
    main()
