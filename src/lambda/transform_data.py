import json
import logging
import urllib.parse
import boto3
import csv
import io

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LOCALSTACK_ENDPOINT = "http://host.docker.internal:4566"
RAW_BUCKET = "nyc-taxi-raw-zone"
CURATED_BUCKET = "nyc-taxi-curated-zone"

s3_client = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

def lambda_handler(event, context):
    logger.info("Lambda function triggered by S3 event!")
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        logger.info(f"Processing file: {key} from bucket: {bucket}")
        
        # 1. Read the file from the Raw Zone
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # 2. Transform the data using built-in csv module
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)
        
        clean_rows = []
        original_count = 0
        for row in reader:
            original_count += 1
            try:
                fare = float(row.get('fare_amount', 0))
                distance = float(row.get('trip_distance', 0))
                
                # Business Logic: Filter out invalid trips
                if fare > 0 and distance > 0:
                    clean_rows.append(row)
            except ValueError:
                logger.warning(f"Skipping row with invalid data: {row}")
                
        logger.info(f"Original rows: {original_count}, Cleaned rows: {len(clean_rows)}")
        
        # 3. Load into the Curated Zone as CSV
        curated_key = key.replace('.csv', '_cleaned.csv')
        
        output = io.StringIO()
        if clean_rows:
            writer = csv.DictWriter(output, fieldnames=clean_rows[0].keys())
            writer.writeheader()
            writer.writerows(clean_rows)
        
        s3_client.put_object(
            Bucket=CURATED_BUCKET,
            Key=curated_key,
            Body=output.getvalue().encode('utf-8'),
            ContentType='text/csv'
        )
        
        logger.info(f"Successfully saved cleaned data to s3://{CURATED_BUCKET}/{curated_key}")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Transformation completed successfully!')
    }
