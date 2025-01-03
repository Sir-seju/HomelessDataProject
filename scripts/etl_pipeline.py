import logging
import os
from io import BytesIO, StringIO

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
AWS_REGION = "us-east-1"
S3_BUCKET = "graystumbucket"
ANXIETY_FILE = "Anxiety/SF_HOMELESS_ANXIETY.csv"
DEMOGRAPHICS_FILE = "Demography/SF_HOMELESS_DEMOGRAPHICS.csv"


def read_csv_from_s3(bucket_name, file_key):
    """
    Read a CSV file from S3 into a Pandas DataFrame.
    """
    logging.info(f"Reading {file_key} from S3 bucket {bucket_name}...")
    s3 = boto3.client("s3", region_name=AWS_REGION)
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_data = response["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        logging.info(f"Successfully read {file_key} from S3.")
        return df
    except Exception as e:
        logging.error(f"Failed to read {file_key} from S3: {e}")
        raise


def normalize_column_names(df):
    """
    Normalize column names by replacing spaces and special characters with underscores.
    """
    logging.info("Normalizing column names...")
    df.columns = (
        df.columns.str.strip()  # Remove leading/trailing whitespace
        .str.replace(" ", "_")  # Replace spaces with underscores
        .str.replace("#", "")  # Remove special characters like #
        .str.replace("/", "_")  # Replace slashes with underscores
    )
    return df


def normalize_ids(anxiety_data, demographics_data):
    """
    Normalize the 'HID' columns in both datasets to ensure compatibility for merging.
    """
    logging.info("Normalizing IDs...")
    anxiety_data["Homeless_ID"] = (
        anxiety_data["Homeless_ID"]
        .str.replace("HM15-", "", regex=False)
        .str.strip()
        .str.zfill(3)
        + "-15"
    )
    demographics_data["HID"] = demographics_data["HID"].str.strip()
    logging.info("IDs normalized successfully.")
    return anxiety_data, demographics_data


def merge_datasets(anxiety_data, demographics_data):
    """
    Merge the anxiety and demographics datasets on the 'HID' column.
    """
    logging.info("Merging datasets...")
    merged_data = pd.merge(
        anxiety_data,
        demographics_data,
        left_on="Homeless_ID",
        right_on="HID",
        how="inner",
    )

    if merged_data.empty:
        logging.warning(
            "The merged dataset is empty. Check if the 'HID' values match in both datasets."
        )
    else:
        logging.info(
            f"Datasets merged successfully. Number of rows: {len(merged_data)}"
        )
    return merged_data


def save_parquet_to_s3(merged_data, bucket_name):
    """
    Save the merged dataset as Parquet files organized by Year and Month, and upload to S3.
    """
    logging.info("Saving merged dataset to S3 as Parquet files...")
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    # Ensure date columns are properly converted
    merged_data["Encounter_Date"] = pd.to_datetime(
        merged_data["Encounter_Date"]
    )  # TIMESTAMP
    merged_data["Registration_Date"] = pd.to_datetime(
        merged_data["Registration_Date"]
    ).dt.date  # DATE
    merged_data["Date_Of_Birth"] = pd.to_datetime(
        merged_data["Date_Of_Birth"]
    ).dt.date  # DATE

    # Extract Year and Month for partitioning
    merged_data["Year"] = merged_data["Encounter_Date"].dt.year.astype(str)
    merged_data["Month"] = (
        merged_data["Encounter_Date"].dt.month.astype(str).str.zfill(2)
    )

    # Define the correct schema
    schema = pa.schema(
        [
            ("Homeless_ID", pa.string()),
            ("Encounter_Date", pa.timestamp("ms")),  # TIMESTAMP for Athena
            ("Anxiety_Lvl", pa.int64()),
            ("Identifier", pa.int64()),
            ("HID", pa.string()),
            ("Registration_Date", pa.date32()),  # DATE for Athena
            ("First_Name", pa.string()),
            ("Last_Name", pa.string()),
            ("Middle_Name", pa.string()),
            ("Date_Of_Birth", pa.date32()),  # DATE for Athena
            ("Gender", pa.string()),
            ("Race1", pa.string()),  # Removed special character #
            ("Shelter", pa.string()),
            ("Year", pa.string()),
            ("Month", pa.string()),
        ]
    )

    # Group data by Year and Month and save Parquet files to S3
    for (year, month), group in merged_data.groupby(["Year", "Month"]):
        table = pa.Table.from_pandas(group, schema=schema)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)

        # Define the S3 key for the Parquet file
        s3_key = f"data/Year={year}/Month={month}/part-{os.urandom(8).hex()}.parquet"
        parquet_buffer.seek(0)

        # Upload the Parquet file to S3
        try:
            s3_client.upload_fileobj(parquet_buffer, bucket_name, s3_key)
            logging.info(f"Uploaded Parquet file to S3: {s3_key}")
        except Exception as e:
            logging.error(
                f"Failed to upload Parquet file for Year={year}, Month={month}: {e}"
            )
            raise


def process_pipeline():
    """
    Main pipeline for data processing.
    """
    try:
        # Step 1: Load datasets from S3
        anxiety_data = read_csv_from_s3(S3_BUCKET, ANXIETY_FILE)
        demographics_data = read_csv_from_s3(S3_BUCKET, DEMOGRAPHICS_FILE)

        # Step 2: Normalize column names
        anxiety_data = normalize_column_names(anxiety_data)
        demographics_data = normalize_column_names(demographics_data)

        # Step 3: Normalize IDs
        anxiety_data, demographics_data = normalize_ids(anxiety_data, demographics_data)

        # Step 4: Merge datasets
        merged_data = merge_datasets(anxiety_data, demographics_data)

        if not merged_data.empty:
            # Step 5: Save outputs to S3 in partitioned format
            save_parquet_to_s3(merged_data, S3_BUCKET)
        else:
            logging.warning(
                "No output files were generated because the merged dataset is empty."
            )

        logging.info("Data processing pipeline completed successfully.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    process_pipeline()
