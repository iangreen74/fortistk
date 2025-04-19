#!/bin/bash

set -e

REGION="us-east-1"
BUCKET_NAME="fortistk-tfstate-us-east-1"
DYNAMODB_TABLE="fortistk-tf-locks"

echo "🔧 Bootstrapping Terraform remote state in $REGION..."

# Step 1: Create S3 bucket (omit LocationConstraint if us-east-1)
if [ "$REGION" == "us-east-1" ]; then
  aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION || echo "⚠️ Bucket may already exist."
else
  aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION || echo "⚠️ Bucket may already exist."
fi

# Step 2: Enable encryption and versioning
aws s3api wait bucket-exists --bucket $BUCKET_NAME

aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Step 3: Create DynamoDB lock table
aws dynamodb create-table \
  --table-name $DYNAMODB_TABLE \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION || echo "⚠️ Table may already exist."

echo "✅ Remote state backend provisioned."
