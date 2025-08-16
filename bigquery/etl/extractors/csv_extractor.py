"""
CSV data extractor - Simple and reliable for manual exports
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .base import DataSourceAdapter


class CSVExtractor(DataSourceAdapter):
    """Extract data from CSV files - perfect for manual Airtable exports"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CSV extractor
        
        Config options:
            - file_path: Path to CSV file
            - date_columns: List of column names to parse as dates
            - incremental_key: Column name for incremental extraction
        """
        super().__init__(config)
        self.file_path = Path(config.get('file_path', ''))
        self.date_columns = config.get('date_columns', [])
        
    def validate_connection(self) -> bool:
        """Check if CSV file exists and is readable"""
        return self.file_path.exists() and self.file_path.suffix == '.csv'
    
    def extract(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from CSV file"""
        if not self.validate_connection():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        
        # Read CSV with date parsing and encoding handling
        try:
            df = pd.read_csv(
                self.file_path,
                parse_dates=self.date_columns if self.date_columns else False,
                encoding='utf-8'
            )
        except UnicodeDecodeError:
            # Try with latin1 encoding if utf-8 fails
            self.logger.warning("UTF-8 decode failed, trying latin1 encoding")
            df = pd.read_csv(
                self.file_path,
                parse_dates=self.date_columns if self.date_columns else False,
                encoding='latin1'
            )
        
        # Apply incremental filter if needed
        if since and self.get_incremental_key():
            key = self.get_incremental_key()
            if key in df.columns:
                df[key] = pd.to_datetime(df[key])
                df = df[df[key] >= since]
                self.logger.info(f"Filtered to {len(df)} records since {since}")
        
        self._metadata['record_count'] = len(df)
        self._metadata['extraction_time'] = datetime.now()
        self._metadata['source_file'] = str(self.file_path)
        
        return df
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extraction metadata"""
        return {
            **self._metadata,
            'source': 'CSV',
            'file_path': str(self.file_path)
        }