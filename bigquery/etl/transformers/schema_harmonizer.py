"""
Schema harmonization for different data sources
Maps varying field names to standardized schema
"""

import pandas as pd
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging


class SchemaHarmonizer:
    """Harmonize schemas from different sources to standard format"""
    
    def __init__(self, mapping_file: Optional[Path] = None):
        """
        Initialize with field mappings
        
        Args:
            mapping_file: Path to YAML file with field mappings
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if mapping_file and mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self.mappings = yaml.safe_load(f)
        else:
            # Default mappings for common fields
            self.mappings = self._get_default_mappings()
            
        self.reverse_mappings = self._create_reverse_mappings()
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """Get default field mappings"""
        return {
            'core_fields': {
                'id': ['ID', 'Id', 'record_id', 'airtable_id'],
                'state': ['State', 'STATE', 'state_code'],
                'bill_number': ['BillNumber', 'Bill Number', 'bill_num'],
                'description': ['Description', 'Summary', 'Bill Summary', 'Bill Description'],
                'year': ['Year', 'year', 'data_year'],
                'created': ['Created', 'created_time'],
                'modified': ['Modified', 'Last Modified', 'modified_time']
            },
            'status_fields': {
                'introduced': ['Introduced', 'Date Introduced', 'IntroducedDate'],
                'enacted': ['Enacted', 'Date Enacted', 'EnactedDate'],
                'dead': ['Dead', 'Is Dead', 'dead_for_year'],
                'vetoed': ['Vetoed', 'VetoedDate'],
                'pending': ['Pending'],
                'passed_first_chamber': ['Passed 1 Chamber', 'Passed1ChamberDate'],
                'passed_second_chamber': ['Passed 2 Chamber'],
                'passed_legislature': ['PassedLegislature']
            },
            'policy_fields': {
                'abortion': ['Abortion', 'abortion_related'],
                'contraception': ['Contraception', 'contraception_related'],
                'period_products': ['Period Products'],
                'incarceration': ['Incarceration'],
                'medication_abortion': ['Medication Abortion'],
                'telehealth': ['Telehealth'],
                'insurance': ['Insurance'],
                'family_planning': ['Family Planning'],
                'sex_ed': ['Sex Ed'],
                'youth': ['Youth'],
                'pregnancy': ['Pregnancy']
            },
            'intent_fields': {
                'positive': ['Positive'],
                'neutral': ['Neutral'],
                'restrictive': ['Restrictive']
            },
            'bill_type_fields': {
                'bill_type': ['BillType'],
                'legislation': ['Legislation'],
                'resolution': ['Resolution'],
                'ballot_initiative': ['Ballot Initiative'],
                'constitutional_amendment': ['Constitutional Amendment'],
                'court_case': ['Court Case']
            },
            'description_fields': {
                'bill_description': ['BillDescription', 'Bill Description'],
                'internal_summary': ['Internal Summary'],
                'website_blurb': ['WebsiteBlurb']
            }
        }
    
    def _create_reverse_mappings(self) -> Dict[str, str]:
        """Create reverse mapping from variants to standard names"""
        reverse = {}
        
        for category in self.mappings.values():
            if isinstance(category, dict):
                for standard_name, variants in category.items():
                    if isinstance(variants, list):
                        for variant in variants:
                            reverse[variant.lower()] = standard_name
                            
        return reverse
    
    def harmonize(self, df: pd.DataFrame, source_type: str = 'unknown') -> pd.DataFrame:
        """
        Harmonize dataframe to standard schema
        
        Args:
            df: Input dataframe
            source_type: Type of source for specific handling
            
        Returns:
            Harmonized dataframe
        """
        self.logger.info(f"Harmonizing {len(df)} records from {source_type}")
        
        # Create mapping of current columns to standard names
        column_mapping = {}
        unmapped_columns = []
        seen_targets = set()
        
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in self.reverse_mappings:
                target = self.reverse_mappings[col_lower]
                # Check if we've already mapped to this target
                if target in seen_targets:
                    # Keep original name with suffix to avoid duplicates
                    column_mapping[col] = f"{col.lower().replace(' ', '_')}_orig"
                    self.logger.debug(f"Duplicate mapping for {target}, keeping {col} as {column_mapping[col]}")
                else:
                    column_mapping[col] = target
                    seen_targets.add(target)
            else:
                # Keep original name if no mapping found
                unmapped_columns.append(col)
                column_mapping[col] = col.lower().replace(' ', '_')
        
        if unmapped_columns:
            self.logger.warning(f"Unmapped columns: {unmapped_columns}")
        
        # Rename columns
        df_harmonized = df.rename(columns=column_mapping)
        
        # Apply source-specific transformations
        if source_type == 'airtable':
            df_harmonized = self._harmonize_airtable(df_harmonized)
        
        # Ensure required fields exist with proper defaults
        df_harmonized = self._ensure_required_fields(df_harmonized)
        
        return df_harmonized
    
    def _harmonize_airtable(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Airtable-specific harmonization"""
        # Handle Airtable's linked record format
        if 'issuing_agency' in df.columns:
            # Extract first agency if it's a list
            df['issuing_agency'] = df['issuing_agency'].apply(
                lambda x: x[0] if isinstance(x, list) and x else x
            )
        
        return df
    
    def _ensure_required_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required fields exist with proper defaults"""
        # Get lowercase version of all columns for case-insensitive check
        existing_cols_lower = [col.lower() for col in df.columns]
        
        # Status fields default to False
        status_fields = ['introduced', 'enacted', 'dead', 'vetoed', 
                        'seriously_considered', 'passed_first_chamber']
        
        for field in status_fields:
            if field not in existing_cols_lower:
                df[field] = False
        
        # Policy fields default to None (unknown)
        policy_fields = ['abortion', 'contraception', 'period_products', 
                        'incarceration']
        
        for field in policy_fields:
            if field not in existing_cols_lower:
                df[field] = None
        
        return df
    
    def get_standard_schema(self) -> Dict[str, str]:
        """Get the standard schema definition"""
        return {
            # Core fields
            'id': 'string',
            'state': 'string',
            'bill_number': 'string',
            'description': 'string',
            'year': 'integer',
            
            # Status fields
            'introduced': 'boolean',
            'enacted': 'boolean',
            'dead': 'boolean',
            'vetoed': 'boolean',
            
            # Policy fields
            'abortion': 'boolean',
            'contraception': 'boolean',
            'period_products': 'boolean',
            
            # Metadata
            'created_time': 'timestamp',
            'modified_time': 'timestamp'
        }