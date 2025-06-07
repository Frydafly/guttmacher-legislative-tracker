#!/usr/bin/env python3
"""
Consolidated Historical Data Pipeline

A production-ready pipeline that combines the best features of all approaches:
- Reliable extraction using mdbtools (cross-platform)
- Configurable processing modes (simple/advanced)
- Comprehensive error handling and logging
- BigQuery optimization with batch loading
- Data quality validation and monitoring
- Flexible output options for analytics

Usage:
    python consolidated_pipeline.py              # Simple mode
    python consolidated_pipeline.py --advanced   # Advanced transformations
    python consolidated_pipeline.py --validate   # Validation only
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from tqdm import tqdm

# Setup enhanced logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure structured logging with timestamps and context."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Ensure logs directory exists
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                logs_dir / "pipeline.log",
                mode="a"
            )
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


class ConsolidatedPipeline:
    """Production-ready historical data pipeline with comprehensive features."""
    
    def __init__(self, project_id: str, dataset_id: str, mode: str = "simple"):
        """
        Initialize pipeline with comprehensive configuration.
        
        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID  
            mode: Processing mode - 'simple', 'advanced', or 'validate'
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.mode = mode
        
        # Initialize BigQuery client with optimizations
        self.bq_client = bigquery.Client(
            project=project_id,
            default_query_job_config=bigquery.QueryJobConfig(
                use_query_cache=True,
                maximum_bytes_billed=10 * 1024**3  # 10GB limit
            )
        )
        
        # Directory setup with proper structure
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data" / "historical"
        self.staging_path = self.base_path / "data" / "staging"
        self.logs_path = self.base_path / "logs"
        self.processed_path = self.base_path / "data" / "processed"
        
        # Ensure all directories exist
        for path in [self.staging_path, self.logs_path, self.processed_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Pipeline statistics
        self.stats = {
            "files_processed": 0,
            "total_bills": 0,
            "total_categories": 0,
            "errors": [],
            "start_time": datetime.now()
        }
        
        # Load advanced transformer only if needed
        self.transformer = None
        if mode == "advanced":
            try:
                from data_transformer import HistoricalDataTransformer
                self.transformer = HistoricalDataTransformer()
                logger.info("Advanced transformer loaded successfully")
            except ImportError as e:
                logger.warning(f"Advanced transformer not available: {e}")
                logger.warning("Falling back to simple mode")
                self.mode = "simple"

    def validate_environment(self) -> bool:
        """Validate that all required tools and permissions are available."""
        logger.info("Validating environment setup...")
        
        # Check mdbtools availability
        try:
            result = subprocess.run(["mdb-tables", "--help"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✓ mdbtools is available")
            else:
                logger.error("mdbtools not found. Install with: brew install mdbtools")
                return False
        except FileNotFoundError:
            logger.error("mdbtools not found. Install with: brew install mdbtools")
            return False
        
        # Check BigQuery access
        try:
            datasets = list(self.bq_client.list_datasets(max_results=1))
            logger.info("✓ BigQuery access confirmed")
        except Exception as e:
            logger.error(f"BigQuery access failed: {e}")
            return False
        
        # Check if dataset exists
        try:
            self.bq_client.get_dataset(self.dataset_id)
            logger.info(f"✓ Dataset '{self.dataset_id}' exists")
        except Exception:
            logger.warning(f"Dataset '{self.dataset_id}' not found, will create it")
            try:
                dataset = bigquery.Dataset(f"{self.project_id}.{self.dataset_id}")
                dataset.location = "US"
                self.bq_client.create_dataset(dataset)
                logger.info(f"✓ Created dataset '{self.dataset_id}'")
            except Exception as e:
                logger.error(f"Failed to create dataset: {e}")
                return False
        
        # Check data directory
        if not self.data_path.exists():
            logger.error(f"Data directory not found: {self.data_path}")
            return False
            
        mdb_files = list(self.data_path.glob("*.mdb"))
        if not mdb_files:
            logger.warning(f"No .mdb files found in {self.data_path}")
            return False
            
        logger.info(f"✓ Found {len(mdb_files)} .mdb files to process")
        return True
    
    def extract_from_mdb(self, mdb_path: Path) -> Optional[Dict]:
        """Extract all tables from MDB file with comprehensive error handling."""
        logger.info(f"Extracting from {mdb_path.name}")
        
        try:
            # Extract year from filename
            year_match = re.search(r"(\d{4})", mdb_path.name)
            if not year_match:
                error_msg = f"Could not extract year from {mdb_path.name}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
                return None
            
            data_year = int(year_match.group(1))
            
            # Get table list with timeout protection
            try:
                result = subprocess.run(
                    ["mdb-tables", "-1", str(mdb_path)], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
            except subprocess.TimeoutExpired:
                error_msg = f"Timeout extracting table list from {mdb_path.name}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
                return None
            
            if result.returncode != 0:
                error_msg = f"Error listing tables: {result.stderr}"
                logger.error(error_msg)
                self.stats["errors"].append(error_msg)
                return None
            
            tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
            logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")
            
            extracted_data = {}
            
            # Process tables with progress bar
            for table in tqdm(tables, desc=f"Extracting {data_year} tables"):
                csv_file = self.staging_path / f"{data_year}_{table.replace(' ', '_').replace('/', '_')}.csv"
                
                # Export table to CSV with timeout
                try:
                    with open(csv_file, "w", encoding="utf-8") as f:
                        result = subprocess.run(
                            ["mdb-export", str(mdb_path), table],
                            stdout=f,
                            text=True,
                            timeout=120
                        )
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout extracting {table}, skipping")
                    continue
                except Exception as e:
                    logger.warning(f"Error extracting {table}: {e}")
                    continue
                
                if result.returncode == 0 and csv_file.exists():
                    try:
                        # Validate CSV file before reading
                        if csv_file.stat().st_size == 0:
                            logger.warning(f"Empty file generated for {table}")
                            continue
                            
                        df = pd.read_csv(csv_file, encoding="utf-8", low_memory=False)
                        
                        if len(df) == 0:
                            logger.warning(f"No data in {table}")
                            continue
                            
                        logger.info(f"  ✓ {table}: {len(df)} rows, {len(df.columns)} columns")
                        
                        # Categorize table type intelligently
                        table_lower = table.lower()
                        if any(keyword in table_lower for keyword in ["legislative", "bill", "law"]):
                            table_type = "bills"
                        elif any(keyword in table_lower for keyword in ["issue", "category", "area", "policy"]):
                            table_type = "categories"
                        else:
                            table_type = "other"
                        
                        extracted_data[table_type] = {
                            "dataframe": df,
                            "original_table": table,
                            "year": data_year,
                            "csv_file": csv_file
                        }
                        
                    except Exception as e:
                        error_msg = f"Error reading {table}: {e}"
                        logger.error(error_msg)
                        self.stats["errors"].append(error_msg)
                else:
                    logger.warning(f"Failed to extract {table}")
            
            self.stats["files_processed"] += 1
            return extracted_data
            
        except Exception as e:
            error_msg = f"Unexpected error processing {mdb_path.name}: {e}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return None

    def process_simple(self, df: pd.DataFrame, data_year: int, table_type: str) -> pd.DataFrame:
        """Enhanced simple processing with robust cleaning and validation."""
        logger.info(f"Processing {table_type} data for year {data_year} (simple mode)")
        
        if df.empty:
            logger.warning("Empty DataFrame provided for processing")
            return df
        
        df_clean = df.copy()
        original_shape = df_clean.shape
        
        # Add comprehensive metadata
        df_clean["data_year"] = data_year
        df_clean["data_source"] = "Historical"
        df_clean["import_date"] = date.today()
        df_clean["last_updated"] = datetime.now()
        df_clean["processing_mode"] = "simple"
        df_clean["pipeline_version"] = "2.0"
        
        # Enhanced column name cleaning for BigQuery compatibility
        original_columns = list(df_clean.columns)
        cleaned_columns = []
        
        for col in df_clean.columns:
            # Clean and standardize column names
            clean_col = str(col).strip()
            clean_col = re.sub(r"[^\w\s]", "_", clean_col)  # Replace special chars
            clean_col = re.sub(r"\s+", "_", clean_col)  # Replace spaces
            clean_col = re.sub(r"_+", "_", clean_col)  # Collapse multiple underscores
            clean_col = clean_col.strip("_").lower()  # Remove leading/trailing underscores
            
            # Ensure column name doesn't start with number
            if clean_col and clean_col[0].isdigit():
                clean_col = f"col_{clean_col}"
            
            # Handle empty column names
            if not clean_col:
                clean_col = f"unnamed_column_{len(cleaned_columns)}"
            
            cleaned_columns.append(clean_col)
        
        df_clean.columns = cleaned_columns
        
        # Log column renaming
        renamed_cols = [(orig, new) for orig, new in zip(original_columns, cleaned_columns) if orig != new]
        if renamed_cols:
            logger.info(f"Renamed {len(renamed_cols)} columns for BigQuery compatibility")
        
        # Remove completely empty columns and rows
        df_clean = df_clean.dropna(axis=1, how="all")  # Empty columns
        df_clean = df_clean.dropna(axis=0, how="all")  # Empty rows
        
        # Enhanced date processing
        date_columns = [col for col in df_clean.columns if "date" in col.lower()]
        for col in date_columns:
            if df_clean[col].dtype == "object":
                logger.info(f"Converting date column: {col}")
                # Try multiple date formats
                original_values = df_clean[col].copy()
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce", infer_datetime_format=True)
                
                # Report conversion success rate
                success_rate = df_clean[col].notna().sum() / len(df_clean) * 100
                logger.info(f"Date conversion success rate for {col}: {success_rate:.1f}%")
        
        # Enhanced string cleaning
        for col in df_clean.columns:
            if df_clean[col].dtype == "object":
                # Replace various null representations
                null_values = ["nan", "NaN", "NULL", "null", "", "N/A", "n/a", "#N/A"]
                df_clean[col] = df_clean[col].replace(null_values, None)
                
                # Trim whitespace
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace("nan", None)
        
        # Data quality statistics
        final_shape = df_clean.shape
        logger.info(f"Processing complete: {original_shape} -> {final_shape}")
        logger.info(f"Removed {original_shape[1] - final_shape[1]} empty columns")
        logger.info(f"Removed {original_shape[0] - final_shape[0]} empty rows")
        
        return df_clean

    def process_advanced(self, df: pd.DataFrame, data_year: int, table_type: str) -> pd.DataFrame:
        """Advanced processing with full transformation pipeline."""
        logger.info(f"Processing {table_type} data for year {data_year} (advanced mode)")
        
        if not self.transformer:
            logger.warning("Advanced transformer not available, falling back to simple processing")
            return self.process_simple(df, data_year, table_type)
        
        try:
            if table_type == "bills":
                result = self.transformer.transform_historical_data(df, data_year, "state_legislative_table")
            elif table_type == "categories":
                result = self.transformer.transform_historical_data(df, data_year, "specific_issue_areas")
            else:
                logger.info(f"No advanced transformation available for {table_type}, using simple processing")
                result = self.process_simple(df, data_year, table_type)
            
            # Add advanced processing metadata
            result["processing_mode"] = "advanced"
            result["transformation_applied"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Advanced processing failed for {table_type}: {e}")
            logger.info("Falling back to simple processing")
            return self.process_simple(df, data_year, table_type)

    def load_to_bigquery(self, df: pd.DataFrame, table_name: str, mode: str = "replace") -> bool:
        """Load DataFrame to BigQuery with optimized configuration and error handling."""
        if df.empty:
            logger.warning(f"Empty DataFrame provided for table {table_name}")
            return False
            
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        logger.info(f"Loading {len(df)} rows to {table_id}")
        
        # Configure load job with optimizations
        write_disposition = "WRITE_TRUNCATE" if mode == "replace" else "WRITE_APPEND"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True,
            # Optimization settings
            create_disposition="CREATE_IF_NEEDED",
            allow_quoted_newlines=True,
            allow_jagged_rows=False,
            ignore_unknown_values=False,
            max_bad_records=100  # Allow some bad records but track them
        )
        
        if mode == "append":
            job_config.schema_update_options = [
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
            ]
        
        try:
            # Pre-process DataFrame for BigQuery compatibility
            df_for_bq = self._prepare_dataframe_for_bigquery(df)
            
            # Load with progress tracking
            job = self.bq_client.load_table_from_dataframe(
                df_for_bq, table_id, job_config=job_config
            )
            
            # Wait for job completion with timeout
            job.result(timeout=300)  # 5 minute timeout
            
            # Verify load success
            table = self.bq_client.get_table(table_id)
            logger.info(f"✓ Successfully loaded {len(df)} rows to {table_name}")
            logger.info(f"  Table now contains {table.num_rows} total rows")
            
            # Log any load warnings
            if job.errors:
                logger.warning(f"Load completed with {len(job.errors)} errors/warnings")
                for error in job.errors[:5]:  # Log first 5 errors
                    logger.warning(f"  {error}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error loading to {table_name}: {e}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False
    
    def _prepare_dataframe_for_bigquery(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for optimal BigQuery loading."""
        df_clean = df.copy()
        
        # Handle problematic data types
        for col in df_clean.columns:
            # Convert mixed-type columns to strings
            if df_clean[col].dtype == "object":
                # Check for mixed types (numbers and strings)
                non_null_values = df_clean[col].dropna()
                if len(non_null_values) > 0:
                    # Convert everything to string for consistency
                    df_clean[col] = df_clean[col].astype(str)
                    df_clean[col] = df_clean[col].replace("nan", None)
            
            # Handle datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                # Convert to string to avoid timezone issues
                df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                df_clean[col] = df_clean[col].replace("NaT", None)
        
        # Remove any remaining problematic columns
        problematic_cols = []
        for col in df_clean.columns:
            if df_clean[col].dtype.name.startswith('complex'):
                problematic_cols.append(col)
        
        if problematic_cols:
            logger.warning(f"Removing problematic columns: {problematic_cols}")
            df_clean = df_clean.drop(columns=problematic_cols)
        
        return df_clean

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

    def save_pipeline_state(self) -> None:
        """Save pipeline execution state for monitoring and resumption."""
        state_file = self.processed_path / f"pipeline_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        state = {
            "execution_id": datetime.now().isoformat(),
            "mode": self.mode,
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "stats": {
                **self.stats,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.stats["start_time"]).total_seconds()
            }
        }
        
        try:
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"Pipeline state saved to {state_file}")
        except Exception as e:
            logger.error(f"Failed to save pipeline state: {e}")
    
    def run_pipeline(self) -> bool:
        """Execute the complete consolidated pipeline with comprehensive monitoring."""
        logger.info(f"Starting consolidated pipeline v2.0 in {self.mode} mode")
        logger.info(f"Target: {self.project_id}.{self.dataset_id}")
        
        try:
            # Validate environment before starting
            if not self.validate_environment():
                logger.error("Environment validation failed")
                return False
            
            if self.mode == "validate":
                logger.info("Validation-only mode: Environment check complete")
                return True
            
            # Find and validate MDB files
            mdb_files = list(self.data_path.glob("*.mdb"))
            if not mdb_files:
                logger.error(f"No MDB files found in {self.data_path}")
                return False
            
            logger.info(f"Found {len(mdb_files)} MDB files to process")
            
            # Process each file with comprehensive tracking
            processed_years = []
            
            for mdb_file in sorted(mdb_files):
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing {mdb_file.name} ({mdb_file.stat().st_size / 1024 / 1024:.1f} MB)")
                logger.info(f"{'='*60}")
                
                file_start_time = datetime.now()
                extracted_data = self.extract_from_mdb(mdb_file)
                
                if not extracted_data:
                    logger.warning(f"No data extracted from {mdb_file.name}")
                    continue
                
                data_year = None
                file_success = True
                
                for table_type, data in extracted_data.items():
                    df = data["dataframe"]
                    data_year = data["year"]
                    
                    logger.info(f"Processing {table_type} table: {data['original_table']}")
                    
                    # Process based on mode
                    try:
                        if self.mode == "advanced":
                            processed_df = self.process_advanced(df, data_year, table_type)
                        else:
                            processed_df = self.process_simple(df, data_year, table_type)
                        
                        # Generate descriptive table name
                        table_name = f"consolidated_{table_type}_{data_year}"
                        
                        # Load to BigQuery
                        success = self.load_to_bigquery(processed_df, table_name)
                        
                        if success:
                            if table_type == "bills":
                                self.stats["total_bills"] += len(processed_df)
                            elif table_type == "categories":
                                self.stats["total_categories"] += len(processed_df)
                        else:
                            file_success = False
                            
                    except Exception as e:
                        error_msg = f"Error processing {table_type} from {mdb_file.name}: {e}"
                        logger.error(error_msg)
                        self.stats["errors"].append(error_msg)
                        file_success = False
                
                if data_year and file_success:
                    processed_years.append(data_year)
                    file_duration = datetime.now() - file_start_time
                    logger.info(f"✓ File processed successfully in {file_duration.total_seconds():.1f}s")
                else:
                    logger.warning(f"✗ File processing incomplete: {mdb_file.name}")
            
            # Create union tables and views if we have data
            if processed_years:
                logger.info(f"\n{'='*60}")
                logger.info("Creating Union Tables and Analytics Views")
                logger.info(f"{'='*60}")
                
                union_success = self.create_union_tables()
                view_success = self.create_analytics_views()
                
                # Generate final report
                self._generate_final_report(processed_years)
                
                # Save pipeline state
                self.save_pipeline_state()
                
                return union_success and view_success
            else:
                logger.error("No data was successfully processed")
                self.save_pipeline_state()
                return False
                
        except Exception as e:
            error_msg = f"Critical pipeline error: {e}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
            self.save_pipeline_state()
            return False
    
    def _generate_final_report(self, processed_years: List[int]) -> None:
        """Generate comprehensive final execution report."""
        duration = datetime.now() - self.stats["start_time"]
        
        logger.info(f"\n{'='*80}")
        logger.info("CONSOLIDATED PIPELINE EXECUTION REPORT")
        logger.info(f"{'='*80}")
        logger.info(f"Execution Mode: {self.mode}")
        logger.info(f"Target Dataset: {self.project_id}.{self.dataset_id}")
        logger.info(f"Execution Time: {duration.total_seconds():.1f} seconds")
        logger.info(f"")
        logger.info(f"DATA PROCESSED:")
        logger.info(f"  Years: {sorted(processed_years)}")
        logger.info(f"  Files: {self.stats['files_processed']}")
        logger.info(f"  Total Bills: {self.stats['total_bills']:,}")
        logger.info(f"  Total Categories: {self.stats['total_categories']:,}")
        
        if self.stats["errors"]:
            logger.info(f"")
            logger.info(f"ERRORS ({len(self.stats['errors'])}):") 
            for i, error in enumerate(self.stats["errors"][:10], 1):
                logger.info(f"  {i}. {error}")
            if len(self.stats["errors"]) > 10:
                logger.info(f"  ... and {len(self.stats['errors']) - 10} more errors")
        
        logger.info(f"")
        logger.info(f"BIGQUERY TABLES CREATED:")
        logger.info(f"  - consolidated_bills_YYYY (per year)")
        logger.info(f"  - consolidated_categories_YYYY (per year)")
        logger.info(f"  - historical_bills_union (all years)")
        logger.info(f"  - historical_categories_union (all years)")
        logger.info(f"")
        logger.info(f"ANALYTICS VIEWS:")
        logger.info(f"  - v_bills_summary (aggregated statistics)")
        logger.info(f"  - v_bills_trends (year-over-year analysis)")
        logger.info(f"")
        logger.info(f"STATUS: {'SUCCESS' if not self.stats['errors'] else 'COMPLETED WITH ERRORS'}")
        logger.info(f"READY FOR: Looker Studio, Data Analysis, Reporting")
        logger.info(f"{'='*80}")


def main():
    """Run the consolidated pipeline with comprehensive CLI options."""
    parser = argparse.ArgumentParser(
        description="Consolidated Historical Data Pipeline v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python consolidated_pipeline.py                    # Simple mode
  python consolidated_pipeline.py --advanced        # Advanced transformations  
  python consolidated_pipeline.py --validate        # Environment validation only
  python consolidated_pipeline.py --log-level DEBUG # Enable debug logging
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["simple", "advanced", "validate"],
        default="simple",
        help="Processing mode (default: simple)"
    )
    parser.add_argument(
        "--advanced", 
        action="store_const", 
        const="advanced", 
        dest="mode",
        help="Use advanced transformation pipeline"
    )
    parser.add_argument(
        "--validate", 
        action="store_const", 
        const="validate", 
        dest="mode",
        help="Validate environment only, don't process data"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    parser.add_argument(
        "--project-id",
        help="Override GCP project ID from environment"
    )
    parser.add_argument(
        "--dataset-id",
        help="Override BigQuery dataset ID from environment"
    )
    
    args = parser.parse_args()
    
    # Setup logging with specified level
    global logger
    logger = setup_logging(args.log_level)
    
    # Load environment configuration
    load_dotenv()
    
    PROJECT_ID = args.project_id or os.getenv("GCP_PROJECT_ID")
    DATASET_ID = args.dataset_id or os.getenv("BQ_DATASET_ID", "legislative_tracker_staging")
    
    # Validate configuration
    if not PROJECT_ID or PROJECT_ID == "your-actual-project-id":
        logger.error("GCP_PROJECT_ID not configured")
        logger.error("Set in .env file or use --project-id parameter")
        return 1
    
    logger.info(f"Consolidated Historical Data Pipeline v2.0")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Target: {PROJECT_ID}.{DATASET_ID}")
    logger.info(f"Log Level: {args.log_level}")
    
    try:
        # Initialize and run pipeline
        pipeline = ConsolidatedPipeline(PROJECT_ID, DATASET_ID, mode=args.mode)
        success = pipeline.run_pipeline()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())