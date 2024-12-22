import pandas as pd
import boto3

def align_and_merge_datasets(anxiety_file, demographics_file, output_file, bucket_name):
    # Load datasets
    anxiety_data = pd.read_csv(anxiety_file)
    demographics_data = pd.read_csv(demographics_file)

    # Debugging: Print column names to verify
    print("Anxiety Data Columns:", anxiety_data.columns)
    print("Demographics Data Columns:", demographics_data.columns)

    # Merge datasets on HID
    merged_data = pd.merge(
        anxiety_data,
        demographics_data,
        left_on="Homeless ID",
        right_on="HID",
        how="inner"  # Specify the merge strategy
    )

    # Save merged dataset
    merged_data.to_csv(output_file, index=False)
    print("Merged dataset saved.")

    # Upload to S3
    s3 = boto3.client('s3')
    try:
        s3.upload_file(output_file, bucket_name, output_file)
        print(f"{output_file} successfully uploaded to S3.")
    except Exception as e:
        print(f"Error uploading file: {e}")

# Test function
if __name__ == "__main__":
    align_and_merge_datasets(
        "data/SF_HOMELESS_ANXIETY.csv",
        "data/SF_HOMELESS_DEMOGRAPHICS.csv",
        "merged_dataset.csv",
        "my-data-project-bucket"  # Bucket name passed as a string
    )
