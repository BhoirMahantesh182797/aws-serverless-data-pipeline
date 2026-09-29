import logging
import os
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# LocalStack Configuration
LOCALSTACK_ENDPOINT = "http://localhost:4566"
RAW_BUCKET = "nyc-taxi-raw-zone"
FILE_NAME = "yellow_tripdata_sample.csv"

# Dummy credentials for LocalStack
session = boto3.Session(
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

s3_client = session.client("s3", endpoint_url=LOCALSTACK_ENDPOINT)

def generate_mock_data():
    """Generates a realistic mock NYC Taxi dataset in memory."""
    logging.info("Generating realistic mock NYC Taxi data...")
    
    # Create a small, realistic dataset
    data = {
        "VendorID": [1, 2, 1, 2, 1],
        "tpep_pickup_datetime": [
            "2022-01-01 00:30:00", "2022-01-01 01:15:00", 
            "2022-01-01 02:00:00", "2022-01-01 03:45:00", "2022-01-01 04:30:00"
        ],
        "tpep_dropoff_datetime": [
            "2022-01-01 00:45:00", "2022-01-01 01:30:00", 
            "2022-01-01 02:20:00", "2022-01-01 04:00:00", "2022-01-01 05:00:00"
        ],
        "passenger_count": [1, 2, 1, 4, 1],
        "trip_distance": [2.5, 3.1, 1.8, 5.2, 2.0],
        "fare_amount": [12.50, 15.00, 9.50, 22.00, 10.50],
        "tip_amount": [2.50, 3.00, 0.00, 4.50, 2.00],
        "total_amount": [15.80, 19.35, 10.30, 28.80, 13.30]
    }
    
    df = pd.DataFrame(data)
    
    # Convert to CSV string in memory (no need to save to disk!)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def upload_to_s3(csv_string, bucket, s3_key):
    """Uploads a string directly to an S3 bucket."""
    logging.info(f"Uploading data to s3://{bucket}/{s3_key}...")
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=csv_string.encode('utf-8'),
            ContentType='text/csv'
        )
        logging.info("✅ Successfully uploaded to S3!")
    except ClientError as e:
        logging.error(f"Failed to upload to S3: {e}")
        raise

if __name__ == "__main__":
    logging.info("🚀 Starting Extract & Load Process...")
    
    # 1. Extract (Generate mock data in memory)
    csv_data = generate_mock_data()
    
    # 2. Load (Upload directly to S3 Raw Zone)
    upload_to_s3(csv_data, RAW_BUCKET, FILE_NAME)
    
    logging.info("🎉 Extract & Load Process Completed Successfully!")