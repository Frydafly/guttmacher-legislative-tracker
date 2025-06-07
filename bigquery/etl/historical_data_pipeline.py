#!/usr/bin/env python3
"""
Complete historical data pipeline: Extract -> Transform -> Load -> Union -> Analytics Views
Designed for inconsistent historical MDB data with Looker Studio output.
"""

import json
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from data_transformer import HistoricalDataTransformer
from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HistoricalDataPipeline:
    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
        self.transformer = HistoricalDataTransformer()

        # Directory setup
        self.data_path = Path(__file__).parent.parent / "data" / "historical"
        self.staging_path = Path(__file__).parent.parent / "data" / "staging"
        self.staging_path.mkdir(exist_ok=True)

        # Table naming
        self.staging_table_prefix = "staging_historical"
        self.union_table_name = "historical_bills_union"
        self.analytics_table_name = "analytics_bills_view"

    def extract_and_transform_mdb(self, mdb_path):
        """Extract MDB data and apply transformations."""
        logger.info(f"Processing {mdb_path.name}")

        # Extract year from filename
        year_match = re.search(r"(\d{4})", mdb_path.name)
        if not year_match:
            logger.error(f"Could not extract year from {mdb_path.name}")
            return None

        data_year = int(year_match.group(1))

        # Extract tables using mdbtools
        result = subprocess.run(
            ["mdb-tables", "-1", str(mdb_path)], capture_output=True, text=True
        )

        if result.returncode != 0:
            logger.error(f"Error listing tables: {result.stderr}")
            return None

        tables = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]

        transformed_data = {}

        for table in tables:
            logger.info(f"Processing table: {table}")

            # Export to CSV
            csv_file = self.staging_path / f"{data_year}_{table.replace(' ', '_')}.csv"
            with open(csv_file, "w") as f:
                result = subprocess.run(
                    ["mdb-export", str(mdb_path), table], stdout=f, text=True
                )

            if result.returncode != 0:
                logger.error(f"Failed to extract {table}")
                continue

            # Load and transform data
            try:
                df = pd.read_csv(csv_file)

                if "legislative" in table.lower():
                    # This is the main bills table
                    transformed_df = self.transformer.transform_historical_data(
                        df, data_year, "state_legislative_table"
                    )
                    transformed_data["bills"] = transformed_df

                elif "issue" in table.lower() or "category" in table.lower():
                    # This is the policy categories reference table
                    transformed_df = self.transformer.transform_historical_data(
                        df, data_year, "specific_issue_areas"
                    )
                    transformed_data["categories"] = transformed_df

                logger.info(f"Transformed {table}: {len(transformed_df)} rows")

            except Exception as e:
                logger.error(f"Error transforming {table}: {e}")
                continue

        return transformed_data, data_year

    def load_to_staging_tables(self, transformed_data, data_year):
        """Load transformed data to BigQuery staging tables."""
        results = {}

        for table_type, df in transformed_data.items():
            table_name = f"{self.staging_table_prefix}_{table_type}_{data_year}"
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

            # Configure job for staging (replace each year's data)
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE", autodetect=True
            )

            try:
                # Clean column names for BigQuery compatibility
                df_for_bq = df.copy()

                # Fix column names
                df_for_bq.columns = df_for_bq.columns.str.replace(" ", "_", regex=False)
                df_for_bq.columns = df_for_bq.columns.str.replace("/", "_", regex=False)
                df_for_bq.columns = df_for_bq.columns.str.replace(
                    "[^A-Za-z0-9_]", "_", regex=True
                )
                df_for_bq.columns = df_for_bq.columns.str.replace(
                    "__+", "_", regex=True
                )
                df_for_bq.columns = df_for_bq.columns.str.strip("_")
                df_for_bq.columns = df_for_bq.columns.str.lower()

                # Convert arrays to JSON strings for BigQuery compatibility
                for col in df_for_bq.columns:
                    if df_for_bq[col].dtype == "object":
                        # Check if column contains lists
                        non_null_vals = df_for_bq[col].dropna()
                        if not non_null_vals.empty:
                            sample_val = non_null_vals.iloc[0]
                            if isinstance(sample_val, list):
                                df_for_bq[col] = df_for_bq[col].apply(
                                    lambda x: (
                                        json.dumps(x) if isinstance(x, list) else x
                                    )
                                )

                job = self.bq_client.load_table_from_dataframe(
                    df_for_bq, table_id, job_config=job_config
                )
                job.result()

                logger.info(f"Loaded {len(df)} rows to {table_id}")
                results[table_type] = {"success": True, "rows": len(df)}

            except Exception as e:
                logger.error(f"Error loading to {table_id}: {e}")
                results[table_type] = {"success": False, "error": str(e)}

        return results

    def create_union_table(self):
        """Create union table combining all historical years."""
        logger.info("Creating union table for all historical data")

        # Find all staging tables for bills
        query = f"""
        SELECT table_name 
        FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES` 
        WHERE table_name LIKE '{self.staging_table_prefix}_bills_%'
        ORDER BY table_name
        """

        staging_tables = []
        try:
            results = self.bq_client.query(query).result()
            staging_tables = [row.table_name for row in results]
        except Exception as e:
            logger.error(f"Error finding staging tables: {e}")
            return False

        if not staging_tables:
            logger.error("No staging tables found")
            return False

        # Build UNION ALL query
        union_queries = []
        for table_name in staging_tables:
            union_queries.append(
                f"""
                SELECT * FROM `{self.project_id}.{self.dataset_id}.{table_name}`
            """
            )

        union_query = " UNION ALL ".join(union_queries)

        # Create the union table
        create_table_query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.{self.union_table_name}` AS
        {union_query}
        """

        try:
            job = self.bq_client.query(create_table_query)
            job.result()

            # Get row count
            count_query = f"SELECT COUNT(*) as total_rows FROM `{self.project_id}.{self.dataset_id}.{self.union_table_name}`"
            result = list(self.bq_client.query(count_query).result())[0]
            total_rows = result.total_rows

            logger.info(
                f"Created union table with {total_rows} total rows from {len(staging_tables)} years"
            )
            return True

        except Exception as e:
            logger.error(f"Error creating union table: {e}")
            return False

    def create_analytics_views(self):
        """Create Looker Studio optimized analytics views."""
        logger.info("Creating analytics views for Looker Studio")

        # Main analytics view - approximate current Airtable structure
        analytics_view_query = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.{self.analytics_table_name}` AS
        SELECT 
            bill_id,
            state,
            bill_type,
            bill_number,
            current_bill_status,
            
            -- Parse JSON arrays back to repeated fields for BigQuery
            CASE 
                WHEN intent IS NOT NULL AND intent != '' 
                THEN ARRAY(SELECT TRIM(JSON_EXTRACT_SCALAR(intent, '$[' || CAST(pos AS STRING) || ']'), '"')
                          FROM UNNEST(GENERATE_ARRAY(0, JSON_ARRAY_LENGTH(intent) - 1)) AS pos
                          WHERE JSON_EXTRACT_SCALAR(intent, '$[' || CAST(pos AS STRING) || ']') IS NOT NULL)
                ELSE ['Neutral']
            END as intent_array,
            
            -- Date fields
            introduction_date,
            last_action,
            passed_1_chamber_date,
            passed_legislature_date,
            vetoed_date,
            enacted_date,
            
            -- Text fields
            COALESCE(website_blurb, title, '') as description,
            
            -- Metadata
            data_year,
            data_source,
            last_updated,
            
            -- Derived flags for easier analysis
            CASE 
                WHEN enacted_date IS NOT NULL THEN 'Enacted'
                WHEN vetoed_date IS NOT NULL THEN 'Vetoed'
                WHEN current_bill_status LIKE '%Dead%' OR current_bill_status LIKE '%Failed%' THEN 'Dead/Failed'
                WHEN current_bill_status LIKE '%Committee%' THEN 'In Committee'
                ELSE COALESCE(current_bill_status, 'Unknown')
            END as status_category,
            
            CASE 
                WHEN enacted_date IS NOT NULL OR vetoed_date IS NOT NULL THEN 'Final Action'
                WHEN passed_legislature_date IS NOT NULL THEN 'Passed Legislature'
                WHEN passed_1_chamber_date IS NOT NULL THEN 'Passed One Chamber'
                WHEN introduction_date IS NOT NULL THEN 'Introduced'
                ELSE 'Unknown Stage'
            END as bill_stage,
            
            -- Time-based fields for trending
            EXTRACT(YEAR FROM introduction_date) as intro_year,
            EXTRACT(MONTH FROM introduction_date) as intro_month,
            EXTRACT(YEAR FROM enacted_date) as enacted_year,
            
            -- Intent flags for easier filtering
            CASE WHEN intent LIKE '%Positive%' THEN TRUE ELSE FALSE END as is_positive,
            CASE WHEN intent LIKE '%Restrictive%' THEN TRUE ELSE FALSE END as is_restrictive,
            CASE WHEN intent LIKE '%Neutral%' OR intent IS NULL THEN TRUE ELSE FALSE END as is_neutral
            
        FROM `{self.project_id}.{self.dataset_id}.{self.union_table_name}`
        WHERE state IS NOT NULL 
          AND bill_number IS NOT NULL
        """

        # Summary statistics view
        summary_view_query = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.analytics_summary_stats` AS
        SELECT 
            data_year,
            state,
            status_category,
            COUNT(*) as bill_count,
            COUNT(CASE WHEN is_positive THEN 1 END) as positive_bills,
            COUNT(CASE WHEN is_restrictive THEN 1 END) as restrictive_bills,
            COUNT(CASE WHEN is_neutral THEN 1 END) as neutral_bills,
            COUNT(CASE WHEN status_category = 'Enacted' THEN 1 END) as enacted_count,
            COUNT(CASE WHEN status_category = 'Vetoed' THEN 1 END) as vetoed_count,
            
            -- Calculate percentages
            ROUND(COUNT(CASE WHEN is_positive THEN 1 END) * 100.0 / COUNT(*), 1) as positive_pct,
            ROUND(COUNT(CASE WHEN is_restrictive THEN 1 END) * 100.0 / COUNT(*), 1) as restrictive_pct,
            ROUND(COUNT(CASE WHEN status_category = 'Enacted' THEN 1 END) * 100.0 / COUNT(*), 1) as enacted_pct
            
        FROM `{self.project_id}.{self.dataset_id}.{self.analytics_table_name}`
        GROUP BY data_year, state, status_category
        """

        # Time series view for trending
        trends_view_query = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.analytics_trends` AS
        SELECT 
            data_year,
            intro_year,
            intro_month,
            state,
            COUNT(*) as bills_introduced,
            COUNT(CASE WHEN status_category = 'Enacted' THEN 1 END) as bills_enacted,
            COUNT(CASE WHEN is_positive THEN 1 END) as positive_bills,
            COUNT(CASE WHEN is_restrictive THEN 1 END) as restrictive_bills,
            
            -- Rolling averages (where possible)
            AVG(COUNT(*)) OVER (
                PARTITION BY state 
                ORDER BY data_year 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) as avg_bills_3yr
            
        FROM `{self.project_id}.{self.dataset_id}.{self.analytics_table_name}`
        WHERE intro_year IS NOT NULL
        GROUP BY data_year, intro_year, intro_month, state
        ORDER BY data_year DESC, state
        """

        # Execute view creation
        views = [
            ("Main Analytics View", analytics_view_query),
            ("Summary Statistics", summary_view_query),
            ("Trends Analysis", trends_view_query),
        ]

        for view_name, query in views:
            try:
                job = self.bq_client.query(query)
                job.result()
                logger.info(f"Created {view_name}")
            except Exception as e:
                logger.error(f"Error creating {view_name}: {e}")

    def run_complete_pipeline(self):
        """Execute the complete pipeline."""
        logger.info("Starting complete historical data pipeline")

        # Step 1: Find and process all MDB files
        mdb_files = list(self.data_path.glob("*.mdb"))
        if not mdb_files:
            logger.error("No MDB files found")
            return

        logger.info(f"Found {len(mdb_files)} MDB files to process")

        # Step 2: Extract, transform, and load each file
        processed_years = []
        for mdb_file in sorted(mdb_files):
            try:
                transformed_data, data_year = self.extract_and_transform_mdb(mdb_file)
                if transformed_data:
                    load_results = self.load_to_staging_tables(
                        transformed_data, data_year
                    )
                    processed_years.append(data_year)

                    # Log results
                    for table_type, result in load_results.items():
                        status = "✓" if result["success"] else "✗"
                        logger.info(
                            f"{status} {data_year} {table_type}: {result.get('rows', 0)} rows"
                        )

            except Exception as e:
                logger.error(f"Error processing {mdb_file.name}: {e}")

        # Step 3: Create union table
        if processed_years:
            union_success = self.create_union_table()

            # Step 4: Create analytics views
            if union_success:
                self.create_analytics_views()

                logger.info("\n" + "=" * 60)
                logger.info("PIPELINE COMPLETE")
                logger.info("=" * 60)
                logger.info(f"Processed years: {sorted(processed_years)}")
                logger.info(f"Union table: {self.dataset_id}.{self.union_table_name}")
                logger.info(
                    f"Main analytics view: {self.dataset_id}.{self.analytics_table_name}"
                )
                logger.info("Ready for Looker Studio connection!")
            else:
                logger.error("Union table creation failed")
        else:
            logger.error("No data was successfully processed")


def main():
    """Run the pipeline with environment configuration."""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    DATASET_ID = os.getenv("BQ_DATASET_ID", "legislative_tracker_staging")

    if not PROJECT_ID or PROJECT_ID == "your-actual-project-id":
        logger.error("Please update GCP_PROJECT_ID in the .env file")
        return

    # Initialize and run pipeline
    pipeline = HistoricalDataPipeline(PROJECT_ID, DATASET_ID)
    pipeline.run_complete_pipeline()


if __name__ == "__main__":
    main()
