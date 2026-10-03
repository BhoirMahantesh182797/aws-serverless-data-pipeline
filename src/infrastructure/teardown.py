import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOCALSTACK_ENDPOINT = "http://localhost:4566"
RAW_BUCKET = "nyc-taxi-raw-zone"
CURATED_BUCKET = "nyc-taxi-curated-zone"
LAMBDA_FUNCTION = "nyc-taxi-transformer"

session = boto3.Session(
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

s3_client = session.client("s3", endpoint_url=LOCALSTACK_ENDPOINT)
lambda_client = session.client("lambda", endpoint_url=LOCALSTACK_ENDPOINT)

def empty_and_delete_bucket(bucket_name):
    logging.info(f"Emptying bucket: {bucket_name}...")
    try:
        # AWS requires buckets to be completely empty before deleting them
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
        
        logging.info(f"Deleting bucket: {bucket_name}...")
        s3_client.delete_bucket(Bucket=bucket_name)
        logging.info(f"✅ Successfully deleted bucket: {bucket_name}")
    except ClientError as e:
        logging.warning(f"Could not delete bucket {bucket_name}: {e}")

def delete_lambda_function(function_name):
    logging.info(f"Deleting Lambda function: {function_name}...")
    try:
        lambda_client.delete_function(FunctionName=function_name)
        logging.info(f"✅ Successfully deleted Lambda function: {function_name}")
    except ClientError as e:
        logging.warning(f"Could not delete Lambda function {function_name}: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting LocalStack Teardown...")
    
    empty_and_delete_bucket(RAW_BUCKET)
    empty_and_delete_bucket(CURATED_BUCKET)
    delete_lambda_function(LAMBDA_FUNCTION)
    
    logging.info("🎉 Teardown Completed! Your local cloud is now completely clean.")