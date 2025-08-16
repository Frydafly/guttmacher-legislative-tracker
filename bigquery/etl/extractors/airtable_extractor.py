"""
Airtable data extractor
Handles data extraction from Airtable via API or webhook payloads
"""

import json
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import requests
from .base import DataSourceAdapter


class AirtableExtractor(DataSourceAdapter):
    """Extract data from Airtable via API or webhook payloads"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Airtable extractor
        
        Config options:
            - mode: 'api' or 'webhook' or 'export'
            - api_key: Airtable API key (for API mode)
            - base_id: Airtable base ID (for API mode)
            - table_name: Airtable table name (for API mode)
            - webhook_path: Path to webhook payload files (for webhook mode)
            - export_path: Path to Airtable CSV export (for export mode)
            - incremental_key: Field name for incremental extraction (e.g., 'Last Modified')
        """
        super().__init__(config)
        self.mode = config.get('mode', 'export')
        
        if self.mode == 'api':
            self.api_key = config.get('api_key')
            self.base_id = config.get('base_id')
            self.table_name = config.get('table_name')
            self.api_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
            
    def validate_connection(self) -> bool:
        """Validate Airtable connection based on mode"""
        try:
            if self.mode == 'api':
                headers = {'Authorization': f'Bearer {self.api_key}'}
                response = requests.get(
                    self.api_url, 
                    headers=headers,
                    params={'maxRecords': 1}
                )
                return response.status_code == 200
                
            elif self.mode == 'webhook':
                webhook_path = Path(self.config.get('webhook_path', ''))
                return webhook_path.exists() and webhook_path.is_dir()
                
            elif self.mode == 'export':
                export_path = Path(self.config.get('export_path', ''))
                return export_path.exists() and export_path.suffix == '.csv'
                
            return False
            
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False
    
    def extract(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from Airtable"""
        if self.mode == 'api':
            return self._extract_via_api(since)
        elif self.mode == 'webhook':
            return self._extract_from_webhook(since)
        elif self.mode == 'export':
            return self._extract_from_export(since)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _extract_via_api(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data using Airtable API"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        all_records = []
        offset = None
        
        while True:
            params = {'pageSize': 100}
            if offset:
                params['offset'] = offset
                
            # Add filter for incremental extraction
            if since and self.get_incremental_key():
                filter_formula = f"{{{{self.get_incremental_key()}}}} >= '{since.isoformat()}'"
                params['filterByFormula'] = filter_formula
            
            response = requests.get(self.api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            data = response.json()
            records = data.get('records', [])
            
            # Extract fields from records
            for record in records:
                row = record['fields'].copy()
                row['airtable_id'] = record['id']
                row['created_time'] = record.get('createdTime')
                all_records.append(row)
            
            # Check if there are more pages
            offset = data.get('offset')
            if not offset:
                break
        
        df = pd.DataFrame(all_records)
        self._metadata['record_count'] = len(df)
        self._metadata['extraction_time'] = datetime.now()
        
        return df
    
    def _extract_from_webhook(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from webhook payload files"""
        webhook_path = Path(self.config.get('webhook_path', ''))
        all_records = []
        
        # Find all JSON files in the webhook directory
        json_files = sorted(webhook_path.glob('*.json'))
        
        for json_file in json_files:
            # Check if file is newer than 'since' timestamp
            if since:
                file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                if file_time < since:
                    continue
            
            with open(json_file, 'r') as f:
                payload = json.load(f)
                
            # Extract records from webhook payload
            # Adjust this based on your webhook payload structure
            if 'records' in payload:
                records = payload['records']
            elif 'data' in payload:
                records = payload['data']
            else:
                records = [payload]
            
            for record in records:
                if isinstance(record, dict):
                    all_records.append(record)
        
        df = pd.DataFrame(all_records)
        self._metadata['record_count'] = len(df)
        self._metadata['files_processed'] = len(json_files)
        self._metadata['extraction_time'] = datetime.now()
        
        return df
    
    def _extract_from_export(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from Airtable CSV export"""
        export_path = Path(self.config.get('export_path', ''))
        
        # Read CSV with proper handling of Airtable's format
        df = pd.read_csv(
            export_path,
            parse_dates=True,
            infer_datetime_format=True
        )
        
        # Apply incremental filter if needed
        if since and self.get_incremental_key() and self.get_incremental_key() in df.columns:
            df[self.get_incremental_key()] = pd.to_datetime(df[self.get_incremental_key()])
            df = df[df[self.get_incremental_key()] >= since]
        
        self._metadata['record_count'] = len(df)
        self._metadata['extraction_time'] = datetime.now()
        self._metadata['source_file'] = str(export_path)
        
        return df
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extraction metadata"""
        return {
            **self._metadata,
            'mode': self.mode,
            'source': 'Airtable'
        }