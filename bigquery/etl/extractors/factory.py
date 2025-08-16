"""
Factory for creating data source extractors
"""

from typing import Dict, Any
from .base import DataSourceAdapter
from .csv_extractor import CSVExtractor
from .airtable_extractor import AirtableExtractor


class ExtractorFactory:
    """Factory for creating appropriate data extractors"""
    
    _extractors = {
        'csv': CSVExtractor,
        'airtable': AirtableExtractor,
        'airtable_api': AirtableExtractor,
        'airtable_webhook': AirtableExtractor,
        'airtable_export': AirtableExtractor,
    }
    
    @classmethod
    def create(cls, source_type: str, config: Dict[str, Any]) -> DataSourceAdapter:
        """
        Create an extractor based on source type
        
        Args:
            source_type: Type of data source (csv, airtable, etc.)
            config: Configuration for the extractor
            
        Returns:
            Configured data source adapter
        """
        if source_type not in cls._extractors:
            raise ValueError(f"Unknown source type: {source_type}")
        
        extractor_class = cls._extractors[source_type]
        
        # Special handling for Airtable modes
        if source_type.startswith('airtable_'):
            mode = source_type.split('_', 1)[1]
            config['mode'] = mode
            
        return extractor_class(config)
    
    @classmethod
    def register(cls, source_type: str, extractor_class: type):
        """Register a new extractor type"""
        cls._extractors[source_type] = extractor_class
    
    @classmethod
    def list_available(cls) -> list:
        """List all available extractor types"""
        return list(cls._extractors.keys())