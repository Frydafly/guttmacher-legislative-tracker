#!/usr/bin/env python3
"""
Shared BigQuery utilities for annual pipeline
"""

from google.cloud import bigquery
import logging

def create_or_update_unified_view(client: bigquery.Client, project_id: str, years: list):
    """Create unified view across all years"""
    logger = logging.getLogger(__name__)
    
    # Generate UNION ALL query for all years
    union_parts = []
    for year in sorted(years):
        union_parts.append(f"SELECT * FROM `{project_id}.legislative_tracker_staging.historical_bills_{year}`")
    
    query = f"""
    CREATE OR REPLACE VIEW `{project_id}.legislative_tracker_historical.all_historical_bills_unified` AS
    {' UNION ALL '.join(union_parts)}
    """
    
    job = client.query(query)
    job.result()
    
    logger.info("✅ Updated unified view with all years")

def refresh_materialized_table(client: bigquery.Client, project_id: str):
    """Refresh materialized table"""
    logger = logging.getLogger(__name__)
    
    query = f"""
    CREATE OR REPLACE TABLE `{project_id}.legislative_tracker_historical.all_historical_bills_materialized` AS
    SELECT * FROM `{project_id}.legislative_tracker_historical.all_historical_bills_unified`
    """
    
    job = client.query(query)
    job.result()
    
    logger.info("✅ Refreshed materialized table")
