#!/usr/bin/env python3
"""
Run the modular ETL pipeline

Usage:
    python run_pipeline.py                           # Run with default config
    python run_pipeline.py --config airtable_export  # Run with specific config
    python run_pipeline.py --source csv --file data/export.csv
    python run_pipeline.py --incremental             # Run incremental update
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add etl module to path
sys.path.insert(0, str(Path(__file__).parent))

from etl import Pipeline


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run ETL pipeline')
    parser.add_argument('--config', help='Config file name (without .json)')
    parser.add_argument('--source', choices=['csv', 'airtable'], help='Source type')
    parser.add_argument('--file', help='Source file path')
    parser.add_argument('--incremental', action='store_true', help='Run incremental')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    load_dotenv()
    
    # Initialize pipeline
    pipeline = Pipeline()
    
    try:
        if args.config:
            # Run from config file
            config_path = Path('config') / f'{args.config}.json'
            if not config_path.exists():
                print(f"Config file not found: {config_path}")
                return 1
            
            stats = pipeline.run_from_config(config_path)
            
        else:
            # Setup from command line arguments
            source_type = args.source or 'csv'
            
            if source_type == 'csv':
                source_config = {
                    'file_path': args.file or 'data/export.csv'
                }
            elif source_type == 'airtable':
                source_config = {
                    'mode': 'export',
                    'export_path': args.file or 'data/airtable_export.csv'
                }
            
            pipeline.setup_source(source_type, source_config)
            
            # Setup destination
            destination_config = {
                'project_id': os.getenv('GCP_PROJECT_ID'),
                'dataset_id': os.getenv('BQ_DATASET_ID', 'legislative_tracker'),
                'table_id': 'bills'
            }
            pipeline.setup_destination(destination_config)
            
            # Run pipeline
            stats = pipeline.run(incremental=args.incremental)
        
        # Print results
        print("\nPipeline completed successfully!")
        print(f"Records extracted: {stats.get('records_extracted', 0)}")
        print(f"Records loaded: {stats.get('records_loaded', 0)}")
        print(f"Duration: {stats.get('duration', 0):.2f} seconds")
        
        return 0
        
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())