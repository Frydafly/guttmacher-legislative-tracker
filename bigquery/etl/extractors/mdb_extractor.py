"""
MDB data extractor for historical Access databases
Wrapper around existing migration logic
"""

import subprocess
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .base import DataSourceAdapter


class MDBExtractor(DataSourceAdapter):
    """Extract data from MDB/Access files using mdbtools"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MDB extractor
        
        Config options:
            - file_path: Path to MDB file
            - table_name: Table to extract (optional, will auto-detect)
        """
        super().__init__(config)
        self.file_path = Path(config.get('file_path', ''))
        self.table_name = config.get('table_name')
    
    def validate_connection(self) -> bool:
        """Check if MDB file exists and mdbtools is installed"""
        if not self.file_path.exists():
            return False
        
        try:
            result = subprocess.run(['mdb-ver'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.error("mdbtools not installed")
            return False
    
    def extract(self, since: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from MDB file"""
        if not self.validate_connection():
            raise FileNotFoundError(f"MDB file not found: {self.file_path}")
        
        # Get table name if not specified
        if not self.table_name:
            tables = self._get_tables()
            self.table_name = self._find_primary_table(tables)
        
        # Export to CSV using mdb-export
        cmd = ['mdb-export', str(self.file_path), self.table_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"mdb-export failed: {result.stderr}")
        
        # Parse CSV output
        import io
        df = pd.read_csv(io.StringIO(result.stdout))
        
        self._metadata['record_count'] = len(df)
        self._metadata['extraction_time'] = datetime.now()
        self._metadata['source_file'] = str(self.file_path)
        self._metadata['table'] = self.table_name
        
        return df
    
    def _get_tables(self) -> list:
        """Get list of tables in MDB file"""
        cmd = ['mdb-tables', '-1', str(self.file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip().split('\n')
    
    def _find_primary_table(self, tables: list) -> str:
        """Find the main data table"""
        # Logic from original migrate.py
        patterns = ['Bills', 'tblBills', 'MainData']
        for pattern in patterns:
            for table in tables:
                if pattern.lower() in table.lower():
                    return table
        return tables[0] if tables else None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extraction metadata"""
        return {
            **self._metadata,
            'source': 'MDB',
            'file_path': str(self.file_path)
        }