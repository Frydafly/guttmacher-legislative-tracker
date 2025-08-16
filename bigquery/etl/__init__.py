"""
ETL Pipeline for Guttmacher Legislative Tracker
Modular, extensible pipeline for processing data from various sources
"""

# Import only what exists
try:
    from .extractors import ExtractorFactory
except ImportError:
    ExtractorFactory = None

try:
    from .transformers import SchemaHarmonizer
except ImportError:
    SchemaHarmonizer = None

try:
    from .loaders import BigQueryLoader
except ImportError:
    BigQueryLoader = None

try:
    from .pipeline import Pipeline
except ImportError:
    Pipeline = None

__all__ = [
    'Pipeline',
    'ExtractorFactory',
    'SchemaHarmonizer',
    'BigQueryLoader'
]