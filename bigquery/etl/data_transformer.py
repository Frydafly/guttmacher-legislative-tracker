#!/usr/bin/env python3
"""
Data transformation pipeline for historical legislative data.
Handles inconsistent schemas, type casting, and standardization.
"""

import pandas as pd
import numpy as np
import yaml
import re
from datetime import datetime, date
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HistoricalDataTransformer:
    def __init__(self, config_path=None):
        """Initialize transformer with field mappings configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'schema' / 'field_mappings.yaml'
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.target_schema = self.config['target_schema']['bills']
        self.mappings = self.config['historical_mappings']
        self.type_config = self.config['type_casting']
        self.standardization = self.config['standardization']
        self.quality_checks = self.config['quality_checks']
    
    def map_columns(self, df, table_type='state_legislative_table'):
        """Map historical column names to standard field names."""
        if table_type not in self.mappings:
            logger.warning(f"No mapping found for table type: {table_type}")
            return df
        
        mapping_rules = self.mappings[table_type]
        column_mapping = {}
        
        # Find best match for each target field
        for target_field, possible_sources in mapping_rules.items():
            for source_field in possible_sources:
                # Case-insensitive matching
                for col in df.columns:
                    if col.lower().strip() == source_field.lower().strip():
                        column_mapping[col] = target_field
                        break
                if target_field in column_mapping.values():
                    break
        
        # Apply mapping
        df_mapped = df.rename(columns=column_mapping)
        
        # Log mapping results
        mapped_fields = list(column_mapping.values())
        logger.info(f"Mapped {len(mapped_fields)} fields: {mapped_fields}")
        
        unmapped_cols = [col for col in df.columns if col not in column_mapping]
        if unmapped_cols:
            logger.warning(f"Unmapped columns: {unmapped_cols}")
        
        return df_mapped
    
    def standardize_dates(self, df):
        """Standardize date columns with multiple format support."""
        date_fields = [col for col in df.columns if 'date' in col.lower()]
        date_formats = self.type_config['dates']['formats']
        null_values = self.type_config['dates']['null_values']
        
        for col in date_fields:
            if col in df.columns:
                logger.info(f"Processing date field: {col}")
                
                # Replace null values
                df[col] = df[col].replace(null_values, np.nan)
                
                # Try each date format
                parsed_dates = pd.Series([np.nan] * len(df), index=df.index)
                
                for date_format in date_formats:
                    mask = parsed_dates.isna() & df[col].notna()
                    if mask.any():
                        try:
                            temp_dates = pd.to_datetime(
                                df.loc[mask, col], 
                                format=date_format, 
                                errors='coerce'
                            )
                            parsed_dates.loc[mask] = temp_dates
                        except Exception as e:
                            logger.debug(f"Date format {date_format} failed for {col}: {e}")
                
                # Final attempt with flexible parsing
                mask = parsed_dates.isna() & df[col].notna()
                if mask.any():
                    try:
                        temp_dates = pd.to_datetime(df.loc[mask, col], errors='coerce')
                        parsed_dates.loc[mask] = temp_dates
                    except:
                        pass
                
                df[col] = parsed_dates.dt.date
                
                # Log parsing success rate
                success_rate = (parsed_dates.notna() & df[col].notna()).sum() / df[col].notna().sum() * 100 if df[col].notna().sum() > 0 else 0
                logger.info(f"Date parsing success rate for {col}: {success_rate:.1f}%")
        
        return df
    
    def standardize_categorical_fields(self, df):
        """Standardize categorical fields like states, bill types, statuses."""
        
        # Standardize states
        if 'state' in df.columns:
            state_mapping = self.standardization.get('states', {})
            df['state'] = df['state'].map(state_mapping).fillna(df['state'])
            df['state'] = df['state'].str.upper().str.strip()
        
        # Standardize bill types
        if 'bill_type' in df.columns:
            bill_type_mapping = self.standardization.get('bill_types', {})
            df['bill_type'] = df['bill_type'].map(bill_type_mapping).fillna(df['bill_type'])
        
        # Standardize statuses
        if 'current_bill_status' in df.columns:
            status_mapping = self.standardization.get('statuses', {})
            df['current_bill_status'] = df['current_bill_status'].map(status_mapping).fillna(df['current_bill_status'])
        
        return df
    
    def infer_intent_from_text(self, text):
        """Basic intent inference from bill text."""
        if pd.isna(text) or not text:
            return ['Neutral']
        
        text_lower = str(text).lower()
        
        positive_keywords = self.standardization['intents']['default_positive_keywords']
        restrictive_keywords = self.standardization['intents']['default_restrictive_keywords']
        
        has_positive = any(keyword in text_lower for keyword in positive_keywords)
        has_restrictive = any(keyword in text_lower for keyword in restrictive_keywords)
        
        if has_positive and not has_restrictive:
            return ['Positive']
        elif has_restrictive and not has_positive:
            return ['Restrictive']
        elif has_positive and has_restrictive:
            return ['Positive', 'Restrictive']  # Mixed intent
        else:
            return ['Neutral']
    
    def add_derived_fields(self, df, data_year):
        """Add fields that don't exist in historical data but are needed for current schema."""
        
        # Add data tracking fields
        df['data_source'] = 'Historical'
        df['data_year'] = int(data_year)
        df['import_date'] = date.today()
        df['last_updated'] = datetime.now()
        
        # Generate bill_id if missing
        if 'bill_id' not in df.columns or df['bill_id'].isna().all():
            df['bill_id'] = df.apply(
                lambda row: f"{row.get('state', 'UNK')}_{data_year}_{row.get('bill_number', '').replace(' ', '')}", 
                axis=1
            )
        
        # Infer intent from available text fields
        text_fields = ['title', 'website_blurb', 'description', 'summary']
        available_text_fields = [col for col in text_fields if col in df.columns]
        
        if available_text_fields and 'intent' not in df.columns:
            df['combined_text'] = df[available_text_fields].fillna('').apply(
                lambda row: ' '.join(row.astype(str)), axis=1
            )
            df['intent'] = df['combined_text'].apply(self.infer_intent_from_text)
            df = df.drop('combined_text', axis=1)
        
        # Default empty arrays for missing multi-select fields
        array_fields = ['policy_categories', 'specific_policies', 'action_type']
        for field in array_fields:
            if field not in df.columns:
                df[field] = [[] for _ in range(len(df))]
        
        return df
    
    def validate_data_quality(self, df):
        """Run data quality checks and log issues."""
        issues = []
        
        # Check required fields
        for field in self.quality_checks['required_fields']:
            if field not in df.columns:
                issues.append(f"Missing required field: {field}")
            elif df[field].isna().all():
                issues.append(f"Required field is all null: {field}")
        
        # Check valid ranges
        for field, range_config in self.quality_checks.get('valid_ranges', {}).items():
            if field in df.columns:
                min_val, max_val = range_config['min'], range_config['max']
                invalid_count = ((df[field] < min_val) | (df[field] > max_val)).sum()
                if invalid_count > 0:
                    issues.append(f"{field} has {invalid_count} values outside valid range [{min_val}, {max_val}]")
        
        # Check valid values
        for field, valid_values in self.quality_checks.get('valid_values', {}).items():
            if field in df.columns:
                invalid_count = (~df[field].isin(valid_values + [np.nan])).sum()
                if invalid_count > 0:
                    issues.append(f"{field} has {invalid_count} invalid values")
        
        # Log issues
        if issues:
            for issue in issues:
                logger.warning(f"Data quality issue: {issue}")
        else:
            logger.info("All data quality checks passed")
        
        return issues
    
    def transform_historical_data(self, df, data_year, table_type='state_legislative_table'):
        """Complete transformation pipeline for historical data."""
        logger.info(f"Transforming {table_type} data for year {data_year}")
        logger.info(f"Input shape: {df.shape}")
        
        # Step 1: Map column names
        df = self.map_columns(df, table_type)
        
        # Step 2: Standardize dates
        df = self.standardize_dates(df)
        
        # Step 3: Standardize categorical fields
        df = self.standardize_categorical_fields(df)
        
        # Step 4: Add derived fields
        df = self.add_derived_fields(df, data_year)
        
        # Step 5: Validate data quality
        self.validate_data_quality(df)
        
        # Step 6: Ensure target schema compliance
        df = self.ensure_target_schema(df)
        
        logger.info(f"Output shape: {df.shape}")
        logger.info(f"Final columns: {list(df.columns)}")
        
        return df
    
    def ensure_target_schema(self, df):
        """Ensure DataFrame matches target schema as closely as possible."""
        target_fields = list(self.target_schema.keys())
        
        # Add missing fields with appropriate defaults
        for field in target_fields:
            if field not in df.columns:
                field_type = self.target_schema[field]
                
                if field_type == 'STRING':
                    df[field] = None
                elif field_type == 'INTEGER':
                    df[field] = None
                elif field_type == 'DATE':
                    df[field] = None
                elif field_type == 'TIMESTAMP':
                    df[field] = None
                elif 'ARRAY' in field_type:
                    df[field] = [[] for _ in range(len(df))]
                else:
                    df[field] = None
        
        # Reorder columns to match target schema
        available_target_fields = [col for col in target_fields if col in df.columns]
        extra_fields = [col for col in df.columns if col not in target_fields]
        
        final_columns = available_target_fields + extra_fields
        df = df[final_columns]
        
        return df


def main():
    """Test the transformer with sample data."""
    # This would typically be called from the main pipeline
    transformer = HistoricalDataTransformer()
    
    # Example usage:
    # df = pd.read_csv('sample_historical_data.csv')
    # transformed_df = transformer.transform_historical_data(df, 2002)
    # print(transformed_df.head())
    
    print("Data transformer initialized successfully")
    print(f"Target schema fields: {list(transformer.target_schema.keys())}")


if __name__ == "__main__":
    main()