"""
Data cleaning utilities for BigQuery compatibility
"""

import pandas as pd
import numpy as np
from typing import Any
import logging


class DataCleaner:
    """Clean and prepare data for BigQuery loading"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def clean_for_bigquery(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean dataframe for BigQuery compatibility
        
        Args:
            df: Input dataframe
            
        Returns:
            Cleaned dataframe
        """
        df_clean = df.copy()
        
        # Replace infinity values
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        
        # Handle date columns
        date_columns = df_clean.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            # Remove timezone info if present
            if hasattr(df_clean[col], 'dt'):
                df_clean[col] = df_clean[col].dt.tz_localize(None)
        
        # Clean string columns
        string_columns = df_clean.select_dtypes(include=['object']).columns
        for col in string_columns:
            # Remove null bytes and control characters
            df_clean[col] = df_clean[col].apply(self._clean_string)
        
        # Ensure column names are BigQuery compatible and unique
        clean_cols = []
        seen_cols = set()
        for col in df_clean.columns:
            clean_name = self._clean_column_name(col)
            # Handle duplicates
            if clean_name in seen_cols:
                i = 1
                while f"{clean_name}_{i}" in seen_cols:
                    i += 1
                clean_name = f"{clean_name}_{i}"
            seen_cols.add(clean_name)
            clean_cols.append(clean_name)
        df_clean.columns = clean_cols
        
        self.logger.info(f"Cleaned {len(df_clean)} rows for BigQuery")
        
        return df_clean
    
    def _clean_string(self, value: Any) -> Any:
        """Clean individual string values"""
        if pd.isna(value):
            return value
        
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove other control characters
        import re
        value = re.sub(r'[\x01-\x1f\x7f]', '', value)
        
        return value.strip() if value else None
    
    def _clean_column_name(self, name: str) -> str:
        """Clean column name for BigQuery compatibility"""
        # Replace spaces and special characters with underscores
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
        
        # Ensure it doesn't start with a number
        if clean_name and clean_name[0].isdigit():
            clean_name = f'col_{clean_name}'
        
        return clean_name.lower()