import logging
from io import StringIO

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
S3_BUCKET = "graystumbucket"  # Replace with your bucket name
ANXIETY_FILE = "Anxiety/SF_HOMELESS_ANXIETY.csv"  # Replace with your anxiety file path
DEMOGRAPHICS_FILE = "Demography/SF_HOMELESS_DEMOGRAPHICS.csv"  # Replace with your demographics file path
OUTPUT_CSV = "merged_homeless_data.csv"  # Name of the output CSV file
OUTPUT_PARQUET = "merged_homeless_data.parquet"  # Name of the output Parquet file


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


def normalize_ids(anxiety_data, demographics_data):
    """
    Normalize the 'HID' columns in both datasets to ensure compatibility for merging.
    """
    logging.info("Normalizing IDs...")
    anxiety_data["Homeless ID"] = (
        anxiety_data["Homeless ID"]
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
        left_on="Homeless ID",
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


def save_to_csv(merged_data, output_csv):
    """
    Save the merged dataset to a CSV file.
    """
    logging.info("Saving merged dataset to CSV...")
    merged_data.to_csv(output_csv, index=False)
    logging.info(f"Dataset saved to CSV: {output_csv}")


def save_to_parquet(merged_data, output_parquet):
    """
    Save the merged dataset to a Parquet file.
    """
    logging.info("Saving merged dataset to Parquet...")
    table = pa.Table.from_pandas(merged_data)
    pq.write_table(table, output_parquet)
    logging.info(f"Dataset saved to Parquet: {output_parquet}")


def upload_to_s3(file_path, bucket_name, s3_key):
    """
    Upload a file to S3.
    """
    logging.info(f"Uploading {file_path} to S3 bucket {bucket_name}...")
    s3 = boto3.client("s3", region_name=AWS_REGION)
    try:
        with open(file_path, "rb") as data:
            s3.upload_fileobj(data, bucket_name, s3_key)
        logging.info(f"Successfully uploaded {file_path} to S3 as {s3_key}.")
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to S3: {e}")
        raise


def process_pipeline():
    """
    Main pipeline for data processing.
    """
    try:
        # Step 1: Load datasets from S3
        anxiety_data = read_csv_from_s3(S3_BUCKET, ANXIETY_FILE)
        demographics_data = read_csv_from_s3(S3_BUCKET, DEMOGRAPHICS_FILE)

        # Step 2: Normalize IDs
        anxiety_data, demographics_data = normalize_ids(anxiety_data, demographics_data)

        # Step 3: Merge datasets
        merged_data = merge_datasets(anxiety_data, demographics_data)

        if not merged_data.empty:
            # Step 4: Save outputs
            save_to_csv(merged_data, OUTPUT_CSV)
            save_to_parquet(merged_data, OUTPUT_PARQUET)

            # Step 5: Upload outputs to S3
            upload_to_s3(OUTPUT_CSV, S3_BUCKET, OUTPUT_CSV)
            upload_to_s3(OUTPUT_PARQUET, S3_BUCKET, OUTPUT_PARQUET)
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
