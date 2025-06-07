#!/usr/bin/env python3
"""
Consolidated Historical Data Pipeline
Combines the best features of all pipeline approaches:
- Simple, reliable extraction using mdbtools
- Optional advanced transformations
- Flexible output options for both raw and processed data
"""

import logging
import os
import re
import subprocess
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConsolidatedPipeline:
    def __init__(self, project_id, dataset_id, mode="simple"):
        """
        Initialize pipeline with different processing modes.
        
        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
            mode: 'simple' for basic extraction, 'advanced' for full transformations
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.mode = mode
        self.bq_client = bigquery.Client(project=project_id)
        
        # Directory setup
        self.data_path = Path(__file__).parent.parent / "data" / "historical"
        self.staging_path = Path(__file__).parent.parent / "data" / "staging"
        self.staging_path.mkdir(exist_ok=True)
        
        # Load advanced transformer only if needed
        if mode == "advanced":
            try:
                from data_transformer import HistoricalDataTransformer
                self.transformer = HistoricalDataTransformer()
            except ImportError:
                logger.warning("Advanced transformer not available, falling back to simple mode")
                self.mode = "simple"

    def extract_from_mdb(self, mdb_path):
        """Extract all tables from MDB file using mdbtools."""
        logger.info(f"Extracting from {mdb_path.name}")
        
        # Extract year from filename
        year_match = re.search(r"(\d{4})", mdb_path.name)
        if not year_match:
            logger.error(f"Could not extract year from {mdb_path.name}")
            return None
        
        data_year = int(year_match.group(1))
        
        # Get table list
        result = subprocess.run(
            ["mdb-tables", "-1", str(mdb_path)], capture_output=True, text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error listing tables: {result.stderr}")
            return None
        
        tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
        logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        extracted_data = {}
        
        for table in tables:
            # Export table to CSV
            csv_file = self.staging_path / f"{data_year}_{table.replace(' ', '_')}.csv"
            
            with open(csv_file, "w") as f:
                result = subprocess.run(
                    ["mdb-export", str(mdb_path), table], stdout=f, text=True
                )
            
            if result.returncode == 0:
                try:
                    df = pd.read_csv(csv_file)
                    logger.info(f"  {table}: {len(df)} rows")
                    
                    # Categorize table type
                    if "legislative" in table.lower():
                        table_type = "bills"
                    elif "issue" in table.lower() or "category" in table.lower():
                        table_type = "categories"
                    else:
                        table_type = "other"
                    
                    extracted_data[table_type] = {
                        "dataframe": df,
                        "original_table": table,
                        "year": data_year
                    }
                    
                except Exception as e:
                    logger.error(f"Error reading {table}: {e}")
            else:
                logger.error(f"Failed to extract {table}")
        
        return extracted_data

    def process_simple(self, df, data_year, table_type):
        """Simple processing - basic cleaning and standardization."""
        df_clean = df.copy()
        
        # Add metadata
        df_clean["data_year"] = data_year
        df_clean["data_source"] = "Historical"
        df_clean["import_date"] = date.today()
        df_clean["last_updated"] = datetime.now()
        
        # Clean column names for BigQuery
        df_clean.columns = [
            re.sub(r"[^\w]", "_", col.strip()).lower().strip("_") 
            for col in df_clean.columns
        ]
        
        # Basic data cleaning
        df_clean = df_clean.dropna(axis=1, how="all")  # Remove empty columns
        
        # Convert obvious date columns
        for col in df_clean.columns:
            if "date" in col and df_clean[col].dtype == "object":
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
        
        # Clean string fields
        for col in df_clean.columns:
            if df_clean[col].dtype == "object":
                df_clean[col] = df_clean[col].astype(str).replace("nan", None)
        
        return df_clean

    def process_advanced(self, df, data_year, table_type):
        """Advanced processing using the transformation pipeline."""
        if table_type == "bills":
            return self.transformer.transform_historical_data(df, data_year, "state_legislative_table")
        elif table_type == "categories":
            return self.transformer.transform_historical_data(df, data_year, "specific_issue_areas")
        else:
            return self.process_simple(df, data_year, table_type)

    def load_to_bigquery(self, df, table_name, mode="replace"):
        """Load DataFrame to BigQuery with flexible options."""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        # Configure load job based on mode
        write_disposition = "WRITE_TRUNCATE" if mode == "replace" else "WRITE_APPEND"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True
        )
        
        if mode == "append":
            job_config.schema_update_options = [
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
            ]
        
        try:
            job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            logger.info(f"✓ Loaded {len(df)} rows to {table_name}")
            return True
        except Exception as e:
            logger.error(f"✗ Error loading to {table_name}: {e}")
            return False

    def create_union_tables(self):
        """Create union tables for each data type."""
        logger.info("Creating union tables")
        
        # Find tables by pattern
        query = f"""
        SELECT table_name 
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES` 
        WHERE table_name LIKE '%bills%' OR table_name LIKE '%categories%'
        ORDER BY table_name
        """
        
        tables = []
        try:
            results = self.bq_client.query(query).result()
            tables = [row.table_name for row in results]
        except Exception as e:
            logger.error(f"Error finding tables: {e}")
            return False
        
        # Group tables by type
        bills_tables = [t for t in tables if "bills" in t and "union" not in t and "summary" not in t]
        category_tables = [t for t in tables if ("categories" in t or "issue" in t) and "union" not in t]
        
        # Create union for bills
        if bills_tables:
            self._create_union_table(bills_tables, "historical_bills_union")
        
        # Create union for categories
        if category_tables:
            self._create_union_table(category_tables, "historical_categories_union")
        
        return True

    def _create_union_table(self, source_tables, union_table_name):
        """Helper to create a union table from multiple source tables."""
        if not source_tables:
            return False
        
        union_queries = []
        for table_name in source_tables:
            union_queries.append(f"SELECT * FROM `{self.project_id}.{self.dataset_id}.{table_name}`")
        
        union_query = " UNION ALL ".join(union_queries)
        
        create_query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.{union_table_name}` AS
        {union_query}
        """
        
        try:
            job = self.bq_client.query(create_query)
            job.result()
            
            # Get row count
            count_query = f"SELECT COUNT(*) as total FROM `{self.project_id}.{self.dataset_id}.{union_table_name}`"
            result = list(self.bq_client.query(count_query).result())[0]
            
            logger.info(f"✓ Created {union_table_name} with {result.total} rows from {len(source_tables)} tables")
            return True
        except Exception as e:
            logger.error(f"✗ Error creating {union_table_name}: {e}")
            return False

    def create_analytics_views(self):
        """Create useful analytics views for both simple and advanced modes."""
        logger.info("Creating analytics views")
        
        # Basic summary view
        summary_view = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.v_bills_summary` AS
        SELECT 
            data_year,
            UPPER(COALESCE(state, '')) as state,
            COUNT(*) as total_bills,
            COUNT(CASE WHEN bill_number IS NOT NULL AND bill_number != '' THEN 1 END) as bills_with_number,
            COUNT(CASE WHEN status LIKE '%Pass%' OR status LIKE '%Enact%' THEN 1 END) as passed_bills,
            COUNT(CASE WHEN status LIKE '%Veto%' THEN 1 END) as vetoed_bills,
            COUNT(CASE WHEN status LIKE '%Dead%' OR status LIKE '%Fail%' THEN 1 END) as failed_bills,
            
            -- Calculate rates
            ROUND(COUNT(CASE WHEN status LIKE '%Pass%' OR status LIKE '%Enact%' THEN 1 END) * 100.0 / COUNT(*), 1) as pass_rate,
            
            MAX(last_updated) as data_updated
        FROM `{self.project_id}.{self.dataset_id}.historical_bills_union`
        WHERE data_year IS NOT NULL
        GROUP BY data_year, state
        ORDER BY data_year DESC, state
        """
        
        # Trend analysis view
        trends_view = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.v_bills_trends` AS
        SELECT 
            data_year,
            COUNT(*) as bills_introduced,
            COUNT(DISTINCT UPPER(COALESCE(state, ''))) as states_active,
            
            -- Status breakdown
            COUNT(CASE WHEN status LIKE '%Pass%' OR status LIKE '%Enact%' THEN 1 END) as enacted,
            COUNT(CASE WHEN status LIKE '%Veto%' THEN 1 END) as vetoed,
            COUNT(CASE WHEN status LIKE '%Dead%' OR status LIKE '%Fail%' THEN 1 END) as failed,
            COUNT(CASE WHEN status NOT LIKE '%Pass%' AND status NOT LIKE '%Enact%' 
                       AND status NOT LIKE '%Veto%' AND status NOT LIKE '%Dead%' 
                       AND status NOT LIKE '%Fail%' THEN 1 END) as other_status,
            
            -- Calculate year-over-year changes
            LAG(COUNT(*)) OVER (ORDER BY data_year) as prev_year_bills,
            COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY data_year) as yoy_change
            
        FROM `{self.project_id}.{self.dataset_id}.historical_bills_union`
        WHERE data_year IS NOT NULL
        GROUP BY data_year
        ORDER BY data_year
        """
        
        views = [
            ("Bills Summary", summary_view),
            ("Bills Trends", trends_view)
        ]
        
        for view_name, query in views:
            try:
                job = self.bq_client.query(query)
                job.result()
                logger.info(f"✓ Created {view_name}")
            except Exception as e:
                logger.error(f"✗ Error creating {view_name}: {e}")

    def run_pipeline(self):
        """Execute the complete consolidated pipeline."""
        logger.info(f"Starting consolidated pipeline in {self.mode} mode")
        
        # Find MDB files
        mdb_files = list(self.data_path.glob("*.mdb"))
        if not mdb_files:
            logger.error("No MDB files found")
            return
        
        logger.info(f"Found {len(mdb_files)} MDB files")
        
        # Process each file
        processed_years = []
        total_bills = 0
        total_categories = 0
        
        for mdb_file in sorted(mdb_files):
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing {mdb_file.name}")
            logger.info(f"{'='*50}")
            
            extracted_data = self.extract_from_mdb(mdb_file)
            if not extracted_data:
                continue
            
            data_year = None
            
            for table_type, data in extracted_data.items():
                df = data["dataframe"]
                data_year = data["year"]
                
                # Process based on mode
                if self.mode == "advanced":
                    processed_df = self.process_advanced(df, data_year, table_type)
                else:
                    processed_df = self.process_simple(df, data_year, table_type)
                
                # Generate table name
                table_name = f"consolidated_{table_type}_{data_year}"
                
                # Load to BigQuery
                success = self.load_to_bigquery(processed_df, table_name)
                
                if success:
                    if table_type == "bills":
                        total_bills += len(processed_df)
                    elif table_type == "categories":
                        total_categories += len(processed_df)
            
            if data_year:
                processed_years.append(data_year)
        
        # Create union tables and views
        if processed_years:
            logger.info(f"\n{'='*50}")
            logger.info("Creating Union Tables and Views")
            logger.info(f"{'='*50}")
            
            self.create_union_tables()
            self.create_analytics_views()
            
            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("CONSOLIDATED PIPELINE COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"Mode: {self.mode}")
            logger.info(f"Years processed: {sorted(processed_years)}")
            logger.info(f"Total bills: {total_bills}")
            logger.info(f"Total categories: {total_categories}")
            logger.info(f"Dataset: {self.dataset_id}")
            logger.info("Ready for analysis and Looker Studio!")
        else:
            logger.error("No data was successfully processed")


def main():
    """Run the consolidated pipeline with configuration options."""
    load_dotenv()
    
    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    DATASET_ID = os.getenv("BQ_DATASET_ID", "legislative_tracker_staging")
    
    if not PROJECT_ID or PROJECT_ID == "your-actual-project-id":
        logger.error("Please update GCP_PROJECT_ID in the .env file")
        return
    
    # Choose processing mode
    import sys
    mode = "simple"
    if len(sys.argv) > 1 and sys.argv[1] == "--advanced":
        mode = "advanced"
    
    logger.info(f"Running in {mode} mode")
    logger.info("Use --advanced flag for full transformation pipeline")
    
    # Initialize and run pipeline
    pipeline = ConsolidatedPipeline(PROJECT_ID, DATASET_ID, mode=mode)
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()