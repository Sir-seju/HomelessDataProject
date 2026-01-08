import logging
from io import BytesIO

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_and_merge_csvs(s3, bucket_name, file_key):
    """
    Retrieve, normalize, align, and merge anxiety and demography CSVs once both files are available.
    Generate Parquet files and update Athena partitions.
    """
    logging.info(f"Processing triggered by file: {file_key}")

    # Determine file type and expected corresponding file
    if "anxiety" in file_key.lower():
        logging.info("Detected anxiety file.")
        corresponding_file_key = file_key.lower().replace("anxiety", "demography")
    elif "demography" in file_key.lower():
        logging.info("Detected demography file.")
        corresponding_file_key = file_key.lower().replace("demography", "anxiety")
    else:
        logging.warning(f"Unknown file type for {file_key}. Skipping.")
        return

    # Check if the corresponding file exists using HeadObject
    try:
        logging.info(f"Checking existence of: {corresponding_file_key}")
        s3.head_object(Bucket=bucket_name, Key=corresponding_file_key)
        logging.info(f"Corresponding file located: {corresponding_file_key}")
    except Exception as e:
        logging.error(f"Error while searching for corresponding file: {e}")
        return

    # Step 1: Load both datasets
    logging.info(f"Reading files: {file_key} and {corresponding_file_key}")
    df1 = read_csv_from_s3(s3, bucket_name, file_key)
    df2 = read_csv_from_s3(s3, bucket_name, corresponding_file_key)

    # Step 2: Normalize the datasets
    logging.info("Normalizing data...")
    if "anxiety" in file_key.lower():
        anxiety_df = normalize_anxiety(df1)
        demography_df = normalize_demography(df2)
    else:
        anxiety_df = normalize_anxiety(df2)
        demography_df = normalize_demography(df1)

    # Step 3: Align and merge
    logging.info("Aligning and merging data...")
    merged_df = pd.merge(
        anxiety_df, demography_df, left_on="Homeless_ID", right_on="HID", how="inner"
    )

    # Step 4: Partition data by Year and Month
    logging.info("Partitioning data...")
    merged_df["Year"] = merged_df["Encounter_Date"].dt.year.astype(str)
    merged_df["Month"] = merged_df["Encounter_Date"].dt.month.astype(str).str.zfill(2)

    # Step 5: Save as Parquet and upload to S3
    logging.info("Uploading Parquet files to S3...")
    upload_parquet_to_s3(s3, bucket_name, merged_df)

    # Step 6: Update Athena partitions
    logging.info("Updating Athena partitions...")
    update_athena_partitions(s3, bucket_name, merged_df)


def read_csv_from_s3(s3, bucket_name, file_key):
    """
    Read a CSV file from S3 into a Pandas DataFrame and normalize column names.
    """
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = response["Body"].read().decode("utf-8")
    df = pd.read_csv(BytesIO(csv_data.encode()))

    # Normalize column names
    logging.info(f"Original columns in {file_key}: {list(df.columns)}")
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("#", "")
        .str.replace("/", "_")
    )
    logging.info(f"Normalized columns in {file_key}: {list(df.columns)}")
    return df


def normalize_anxiety(df):
    """
    Normalize the anxiety data.
    """
    logging.info(f"Columns before normalization: {list(df.columns)}")

    # Normalize IDs
    df["Homeless_ID"] = (
        df["Homeless_ID"].str.replace("HM15-", "", regex=False).str.strip().str.zfill(3)
        + "-15"
    )

    # Ensure Encounter_Date is a proper TIMESTAMP
    df["Encounter_Date"] = pd.to_datetime(df["Encounter_Date"])  # TIMESTAMP

    logging.info("Anxiety data normalized successfully.")
    return df


def normalize_demography(df):
    """
    Normalize the demography data.
    """
    logging.info(f"Columns before normalization: {list(df.columns)}")

    # Normalize IDs
    df["HID"] = df["HID"].str.strip()

    # Convert date columns to DATE type
    df["Registration_Date"] = pd.to_datetime(df["Registration_Date"]).dt.date  # DATE
    df["Date_Of_Birth"] = pd.to_datetime(df["Date_Of_Birth"]).dt.date  # DATE

    logging.info("Demography data normalized successfully.")
    return df


def upload_parquet_to_s3(s3, bucket_name, df):
    """
    Convert DataFrame to Parquet with a defined schema and upload to S3.
    """
    schema = pa.schema(
        [
            ("Homeless_ID", pa.string()),
            ("Encounter_Date", pa.timestamp("ms")),
            ("Anxiety_Lvl", pa.int64()),
            ("Identifier", pa.int64()),
            ("HID", pa.string()),
            ("Registration_Date", pa.date32()),
            ("First_Name", pa.string()),
            ("Last_Name", pa.string()),
            ("Middle_Name", pa.string()),
            ("Date_Of_Birth", pa.date32()),
            ("Gender", pa.string()),
            ("Race1", pa.string()),
            ("Shelter", pa.string()),
            ("Year", pa.string()),
            ("Month", pa.string()),
        ]
    )

    for (year, month), group in df.groupby(["Year", "Month"]):
        table = pa.Table.from_pandas(group, schema=schema)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)

        parquet_key = (
            f"processed_data/Year={year}/Month={month}/part-{year}-{month}.parquet"
        )
        s3.put_object(
            Bucket=bucket_name, Key=parquet_key, Body=parquet_buffer.getvalue()
        )
        logging.info(f"Uploaded Parquet file to: s3://{bucket_name}/{parquet_key}")


def update_athena_partitions(s3, bucket_name, df):
    """
    Add partitions to Athena table based on Year and Month.
    """
    athena = boto3.client("athena", region_name="us-east-1")
    for year, month in df.groupby(["Year", "Month"]).groups.keys():
        query = f"""
        ALTER TABLE homeless_data ADD IF NOT EXISTS 
        PARTITION (Year='{year}', Month='{month}')
        LOCATION 's3://{bucket_name}/processed_data/Year={year}/Month={month}/';
        """
        athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": "default"},
            ResultConfiguration={
                "OutputLocation": f"s3://{bucket_name}/Queries/"
            },
        )
        logging.info(f"Athena partition added for Year={year}, Month={month}")


# if __name__ == "__main__":
#     # Initialize the S3 client
#     s3 = boto3.client("s3")

#     # Replace these with the actual bucket name and file key
#     bucket_name = "graystumbucket"
#     file_key = "new_data/demography/new_demography_data_july.csv"

#     # Call the function
#     process_and_merge_csvs(s3, bucket_name, file_key)
