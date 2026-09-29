import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOCALSTACK_ENDPOINT_URL = "http://localhost:4566"

session = boto3.session.Session(
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

s3_client = session.client('s3', endpoint_url=LOCALSTACK_ENDPOINT_URL)

def create_s3_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logging.info(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logging.error(f"Creating bucket:{bucket_name} ....")

            s3_client.create_bucket(Bucket=bucket_name)
            logging.info(f"Successfully created bucket: {bucket_name}")
        else:
            logging.error(f"Failed to create bucket '{bucket_name}': {e}")
            raise

if __name__ == "__main__":
    logging.info("🚀 Starting LocalStack S3 Infrastructure Setup...")

    raw_bucket = 'nyc-taxi-raw-zone'
    curated_bucket = 'nyc-taxi-curated-zone'

    create_s3_bucket(raw_bucket)
    create_s3_bucket(curated_bucket)

    logging.info("✅ LocalStack S3 Infrastructure Setup Completed.")

    response = s3_client.list_buckets()
    logging.info("Current S3 Bucket in localstack:")
    for bucket in response['Buckets']:
        logging.info(f" - {bucket['Name']}")