import boto3
import logging
from scripts.process_csvs import process_and_merge_csvs

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def lambda_handler(event, context):
    """
    Lambda handler to process uploaded files from S3.
    """
    s3 = boto3.client("s3")

    # Parse the event to get bucket name and file key
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    file_key = event["Records"][0]["s3"]["object"]["key"]

    logging.info(f"Lambda triggered by file: s3://{bucket_name}/{file_key}")

    # Call the processing function with the correct arguments
    process_and_merge_csvs(s3, bucket_name, file_key)