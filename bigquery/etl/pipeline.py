"""
Main ETL pipeline orchestrator
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json

from .extractors import ExtractorFactory
from .transformers import SchemaHarmonizer
from .loaders import BigQueryLoader


class Pipeline:
    """Main ETL pipeline for processing legislative data"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize pipeline with configuration
        
        Args:
            config_path: Path to JSON configuration file
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load configuration
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
        
        # Initialize components
        self.extractor = None
        self.harmonizer = SchemaHarmonizer()
        self.loader = None
        
        # Pipeline state
        self.last_run = None
        self.stats = {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'source': {
                'type': 'csv',
                'config': {
                    'file_path': 'data/export.csv'
                }
            },
            'destination': {
                'project_id': 'your-project',
                'dataset_id': 'legislative_tracker',
                'table_id': 'bills'
            },
            'incremental': {
                'enabled': False,
                'key': 'modified_time'
            }
        }
    
    def setup_source(self, source_type: str, source_config: Dict[str, Any]):
        """
        Configure the data source
        
        Args:
            source_type: Type of source (csv, airtable, etc.)
            source_config: Configuration for the source
        """
        self.extractor = ExtractorFactory.create(source_type, source_config)
        
        if not self.extractor.validate_connection():
            raise ConnectionError(f"Cannot connect to {source_type} source")
        
        self.logger.info(f"Source configured: {source_type}")
    
    def setup_destination(self, destination_config: Dict[str, Any]):
        """
        Configure the destination
        
        Args:
            destination_config: BigQuery configuration
        """
        self.loader = BigQueryLoader(destination_config)
        self.logger.info("Destination configured: BigQuery")
    
    def run(self, incremental: bool = None) -> Dict[str, Any]:
        """
        Run the pipeline
        
        Args:
            incremental: Whether to run incrementally (overrides config)
            
        Returns:
            Pipeline execution statistics
        """
        start_time = datetime.now()
        
        # Determine if running incrementally
        if incremental is None:
            incremental = self.config.get('incremental', {}).get('enabled', False)
        
        self.logger.info(f"Starting pipeline run (incremental={incremental})")
        
        try:
            # Extract
            since = None
            if incremental and self.last_run:
                since = self.last_run
                
            df = self.extractor.extract(since=since)
            self.stats['records_extracted'] = len(df)
            
            # Transform
            df_harmonized = self.harmonizer.harmonize(
                df, 
                source_type=self.config['source']['type']
            )
            
            # Clean for BigQuery
            from .transformers import DataCleaner
            cleaner = DataCleaner()
            df_harmonized = cleaner.clean_for_bigquery(df_harmonized)
            
            self.stats['records_transformed'] = len(df_harmonized)
            
            # Load
            rows_loaded = self.loader.load(
                df_harmonized,
                mode='append' if incremental else 'replace'
            )
            self.stats['records_loaded'] = rows_loaded
            
            # Update state
            self.last_run = datetime.now()
            self.stats['duration'] = (datetime.now() - start_time).total_seconds()
            self.stats['status'] = 'success'
            
            self.logger.info(f"Pipeline completed: {self.stats}")
            
        except Exception as e:
            self.stats['status'] = 'failed'
            self.stats['error'] = str(e)
            self.logger.error(f"Pipeline failed: {e}")
            raise
        
        return self.stats
    
    def run_from_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Run pipeline from a configuration file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Pipeline execution statistics
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Setup components
        self.setup_source(
            config['source']['type'],
            config['source']['config']
        )
        
        self.setup_destination(config['destination'])
        
        # Run pipeline
        return self.run(
            incremental=config.get('incremental', {}).get('enabled', False)
        )
    
    def validate(self) -> bool:
        """Validate pipeline configuration"""
        checks = []
        
        # Check source
        if self.extractor:
            checks.append(self.extractor.validate_connection())
        
        # Check destination
        if self.loader:
            checks.append(self.loader.validate_connection())
        
        return all(checks)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'stats': self.stats,
            'source': self.extractor.get_source_info() if self.extractor else None,
            'destination': self.loader.get_destination_info() if self.loader else None
        }