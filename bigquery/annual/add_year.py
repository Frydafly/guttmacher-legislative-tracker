#!/usr/bin/env python3
"""
Annual Data Import Script - Add new year to BigQuery
Handles both raw archival and harmonized analytical import
"""

import argparse
import logging
import yaml
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent))

from raw_archive import archive_year_raw
from harmonized_import import import_year_harmonized

def main():
    parser = argparse.ArgumentParser(description="Import new year data to BigQuery")
    parser.add_argument("--year", type=int, required=True, help="Year to import")
    parser.add_argument("--config", help="Custom config file (optional)")
    parser.add_argument("--raw-only", action="store_true", help="Only raw import")
    parser.add_argument("--harmonized-only", action="store_true", help="Only harmonized import")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 Starting {args.year} data import...")
    
    # Load configuration
    config_file = args.config or f"../yearly_configs/{args.year}.yaml"
    config_path = Path(__file__).parent / config_file
    
    if not config_path.exists():
        logger.error(f"❌ Configuration file not found: {config_path}")
        return 1
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"📋 Loaded configuration: {config_path.name}")
    
    try:
        # Raw import (archival)
        if not args.harmonized_only and config.get('raw_import', {}).get('enabled', True):
            logger.info(f"📦 Starting raw archival import for {args.year}...")
            archive_year_raw(args.year, config)
            logger.info(f"✅ Raw import completed")
        
        # Harmonized import (analytical)  
        if not args.raw_only and config.get('harmonized_import', {}).get('enabled', True):
            logger.info(f"🔄 Starting harmonized import for {args.year}...")
            import_year_harmonized(args.year, config)
            logger.info(f"✅ Harmonized import completed")
            
        logger.info(f"🎉 {args.year} import completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
