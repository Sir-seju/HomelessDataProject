import os

import boto3

# AWS S3 Configuration
bucket_name = "graystumbucket"
new_data_prefix = "new_data/"

# Test Data
new_test_files = {
    "anxiety/new_test_anxiety_data.csv": """Homeless ID,Encounter Date,Anxiety Lvl,Identifier
HM15-005,2019-06-01,7,4
HM15-006,2019-07-15,5,5
HM15-007,2019-08-20,9,6
HM15-008,2019-09-10,4,7
""",
    "demography/new_test_demography_data.csv": """HID,Registration Date,First Name,Last Name,Middle Name,Date Of Birth,Gender,Race#1,Shelter
005-15,2015-01-15,James,Smith,Michael,1987-06-10,Male,White,Happy Shelter
006-15,2016-03-22,Lisa,Johnson,Ann,1992-04-08,Female,Asian,Hope Center
007-15,2018-07-19,Robert,Brown,Allen,1980-10-30,Male,Black,Billy's Shelter
008-15,2020-12-25,Susan,Davis,Marie,1995-09-14,Female,Hispanic,Safe Haven Shelter
"""
}


def upload_test_files():
    s3 = boto3.client("s3")

    for file_key, content in new_test_files.items():
        s3_key = os.path.join(new_data_prefix, file_key)
        print(f"Uploading {file_key} to s3://{bucket_name}/{s3_key}")
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=content)
        print(f"Uploaded: {s3_key}")


if __name__ == "__main__":
    upload_test_files()
