#!/bin/bash

set -e

REPO="wallet-score-agent"
AWS_REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "🐳 Building Docker image..."
docker build -t $REPO ./agents/$REPO

echo "🏷 Tagging image for ECR..."
docker tag $REPO:latest "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest"

echo "📤 Pushing to ECR..."
docker push "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest"

echo "✅ Push complete."
