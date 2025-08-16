"""
Base classes for data source adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import logging


class DataSourceAdapter(ABC):
    """Abstract base class for all data source adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter with configuration
        
        Args:
            config: Configuration dictionary specific to the data source
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._metadata = {}
        
    @abstractmethod
    def extract(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """
        Extract data from the source
        
        Args:
            since: Optional timestamp for incremental extraction
            
        Returns:
            DataFrame containing the extracted data
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the extraction
        
        Returns:
            Dictionary containing metadata like record count, extraction time, etc.
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the data source is accessible
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    def get_schema(self) -> Dict[str, str]:
        """
        Get the schema of the data source
        
        Returns:
            Dictionary mapping column names to data types
        """
        sample_data = self.extract(since=datetime.now())
        if sample_data.empty:
            return {}
        
        return {
            col: str(dtype) for col, dtype in sample_data.dtypes.items()
        }
    
    def get_incremental_key(self) -> Optional[str]:
        """
        Get the column name used for incremental extraction
        
        Returns:
            Column name or None if incremental extraction not supported
        """
        return self.config.get('incremental_key')
    
    def supports_incremental(self) -> bool:
        """
        Check if this adapter supports incremental extraction
        
        Returns:
            True if incremental extraction is supported
        """
        return self.get_incremental_key() is not None
    
    def get_last_processed_value(self) -> Optional[Any]:
        """
        Get the last processed value for incremental extraction
        
        Returns:
            Last processed value or None
        """
        return self._metadata.get('last_processed_value')
    
    def set_last_processed_value(self, value: Any):
        """
        Set the last processed value for incremental extraction
        
        Args:
            value: The value to store
        """
        self._metadata['last_processed_value'] = value
        
    def get_source_info(self) -> Dict[str, Any]:
        """
        Get information about the data source
        
        Returns:
            Dictionary with source information
        """
        return {
            'type': self.__class__.__name__,
            'config': {k: v for k, v in self.config.items() if 'password' not in k.lower()},
            'supports_incremental': self.supports_incremental(),
            'incremental_key': self.get_incremental_key()
        }