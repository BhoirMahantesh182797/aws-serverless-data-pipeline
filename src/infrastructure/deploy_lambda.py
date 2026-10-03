import logging
import boto3
import zipfile
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOCALSTACK_ENDPOINT = "http://localhost:4566"
LAMBDA_FUNCTION_NAME = "nyc-taxi-transformer"
RAW_BUCKET = "nyc-taxi-raw-zone"

session = boto3.Session(
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

lambda_client = session.client("lambda", endpoint_url=LOCALSTACK_ENDPOINT)
s3_client = session.client("s3", endpoint_url=LOCALSTACK_ENDPOINT)

def create_lambda_function():
    logging.info("Packaging Lambda function...")
    # Zip the lambda_handler.py file
    zip_filename = "/tmp/lambda_function.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write("src/lambda/transform_data.py", arcname="transform_data.py")
    
    with open(zip_filename, 'rb') as f:
        zipped_code = f.read()

    logging.info(f"Creating Lambda function: {LAMBDA_FUNCTION_NAME}...")
    try:
        lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime='python3.9',
            Role='arn:aws:iam::000000000000:role/lambda-role', # Dummy role for LocalStack
            Handler='transform_data.lambda_handler',
            Code={'ZipFile': zipped_code},
            Timeout=30,
            Environment={
                'Variables': {
                    'LOCALSTACK_ENDPOINT': 'http://host.docker.internal:4566'
                }
            }
        )
        logging.info("✅ Lambda function created successfully!")
    except lambda_client.exceptions.ResourceConflictException:
        logging.info("ℹ️ Lambda function already exists, updating code...")
        lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zipped_code
        )

def attach_s3_trigger():
    logging.info(f"Attaching S3 trigger from {RAW_BUCKET} to Lambda...")
    # 1. Give S3 permission to invoke the Lambda
    lambda_client.add_permission(
        FunctionName=LAMBDA_FUNCTION_NAME,
        StatementId='s3-trigger-permission',
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn=f'arn:aws:s3:::{RAW_BUCKET}'
    )
    
    # 2. Configure the S3 bucket to send events to Lambda
    s3_client.put_bucket_notification_configuration(
        Bucket=RAW_BUCKET,
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': f'arn:aws:lambda:us-east-1:000000000000:function:{LAMBDA_FUNCTION_NAME}',
                    'Events': ['s3:ObjectCreated:*']
                }
            ]
        }
    )
    logging.info("✅ S3 trigger attached successfully!")

if __name__ == "__main__":
    logging.info("🚀 Starting Lambda Deployment to LocalStack...")
    create_lambda_function()
    attach_s3_trigger()
    logging.info("🎉 Lambda Deployment Completed!")