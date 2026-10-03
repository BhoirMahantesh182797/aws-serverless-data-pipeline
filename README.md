# ☁️ AWS Serverless Data Pipeline (LocalStack)

An event-driven, serverless data pipeline that automatically ingests, cleans, and stores NYC Taxi trip data. Built to simulate a real-world AWS cloud architecture locally at **$0 cost** using LocalStack.

## 🏗️ Architecture
1. **Extract**: Mock NYC Taxi data is generated and uploaded to the `nyc-taxi-raw-zone` S3 bucket (Bronze layer).
2. **Event Trigger**: An S3 `ObjectCreated` event automatically triggers an AWS Lambda function.
3. **Transform**: The Lambda function reads the CSV, filters out invalid records (e.g., negative fares or zero distance), and cleans the data using Python's built-in libraries (no heavy dependencies like Pandas, ensuring fast, cold-start-friendly Lambda execution).
4. **Load**: The cleaned data is saved as a `_cleaned.csv` file in the `nyc-taxi-curated-zone` S3 bucket (Silver layer).

## 🛠️ Tech Stack
- **Compute**: AWS Lambda (Python 3.9)
- **Storage**: AWS S3 (Raw and Curated zones)
- **Local Development**: LocalStack (v2.3.2) via Docker Compose
- **Infrastructure**: Python (Boto3) & AWS CLI

## 🚀 How to Run Locally

### Prerequisites
- Docker Desktop installed and running
- Python 3.9+ and `pip`
- AWS CLI installed

### 1. Start LocalStack
```bash
docker compose up -d

### 2. Set LocalStack Credentials
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"

### 3. Provision Infrastructure (S3 Buckets)
python src/infrastructure/create_buckets.py

### 4. Deploy Lambda & Attach S3 Trigger
python src/infrastructure/deploy_lambda.py

### 5. Test the Event-Driven Pipeline
Upload a test file to the raw zone:
echo "VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,fare_amount,tip_amount,total_amount
1,2022-01-01 00:30:00,2022-01-01 00:45:00,1,2.5,12.50,2.50,15.80
2,2022-01-01 02:00:00,2022-01-01 02:10:00,1,-1.0,-5.00,0.00,-5.00" > /tmp/test.csv

aws s3 cp /tmp/test.csv s3://nyc-taxi-raw-zone/test.csv --endpoint-url=http://localhost:4566 --region us-east-1

### 6. Verify the Cleaned Data
Check the curated zone to see the transformed output (the row with the negative fare will be filtered out):
aws s3 ls s3://nyc-taxi-curated-zone --endpoint-url=http://localhost:4566 --region us-east-1

💡 Senior Design Decisions
No Pandas in Lambda: Heavy libraries like pandas and pyarrow cause slow Lambda cold starts and require complex packaging. This pipeline uses Python's built-in csv module for maximum performance and reliability in a serverless environment.
LocalStack over Real AWS: Guarantees 100% reproducibility for anyone cloning this repo, with absolutely zero cloud billing risks.
Medallion Architecture: Clearly separates raw (Bronze) and cleaned (Silver) data into distinct S3 buckets.