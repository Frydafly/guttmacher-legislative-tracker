"""
BigQuery data loader
"""

import pandas as pd
from typing import Dict, Any
from google.cloud import bigquery
import logging


class BigQueryLoader:
    """Load data to BigQuery"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BigQuery loader
        
        Config:
            - project_id: GCP project ID
            - dataset_id: BigQuery dataset ID
            - table_id: BigQuery table ID
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.client = bigquery.Client(project=config['project_id'])
        self.table_ref = f"{config['project_id']}.{config['dataset_id']}.{config['table_id']}"
    
    def load(self, df: pd.DataFrame, mode: str = 'replace') -> int:
        """
        Load dataframe to BigQuery
        
        Args:
            df: DataFrame to load
            mode: 'replace' or 'append'
            
        Returns:
            Number of rows loaded
        """
        write_disposition = (
            bigquery.WriteDisposition.WRITE_TRUNCATE 
            if mode == 'replace' 
            else bigquery.WriteDisposition.WRITE_APPEND
        )
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True
        )
        
        job = self.client.load_table_from_dataframe(
            df, 
            self.table_ref,
            job_config=job_config
        )
        
        job.result()  # Wait for job to complete
        
        self.logger.info(f"Loaded {len(df)} rows to {self.table_ref}")
        return len(df)
    
    def validate_connection(self) -> bool:
        """Validate BigQuery connection"""
        try:
            self.client.get_dataset(self.config['dataset_id'])
            return True
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False
    
    def get_destination_info(self) -> Dict[str, Any]:
        """Get destination information"""
        return {
            'type': 'BigQuery',
            'table': self.table_ref
        }