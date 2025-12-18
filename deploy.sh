#!/bin/bash
set -e

echo "=== Price Tracker Deployment Script ==="
echo ""

# Configuration
REGION="eu-west-3"
REPO_NAME="price-tracker"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# Step 1: Clean up existing ECR repository if it exists
echo "[1/5] Checking for existing ECR repository..."
if aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION &> /dev/null; then
    echo "   → Found existing repository, deleting it..."
    aws ecr delete-repository --repository-name $REPO_NAME --region $REGION --force
    echo "   ✓ Deleted"
else
    echo "   → No existing repository found"
fi

# Step 2: Build Docker image
echo ""
echo "[2/6] Building Docker image..."
docker build -t $REPO_NAME .
echo "   ✓ Image built"

# Step 3: Create ECR repository first (before Lambda)
echo ""
echo "[3/6] Creating ECR repository with Terraform..."
cd terraform
~/Downloads/terraform/terraform init -upgrade
~/Downloads/terraform/terraform apply -target=aws_ecr_repository.price_tracker -target=aws_ecr_lifecycle_policy.price_tracker -auto-approve
cd ..
echo "   ✓ ECR repository created"

# Step 4: Push Docker image to ECR
echo ""
echo "[4/6] Pushing Docker image to ECR..."
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

# Login to ECR
aws ecr get-login-password --region $REGION | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Tag and push
docker tag $REPO_NAME:latest $ECR_URL:latest
docker push $ECR_URL:latest
echo "   ✓ Image pushed to ECR"

# Step 5: Deploy rest of infrastructure with Terraform
echo ""
echo "[5/6] Deploying rest of infrastructure (Lambda, DynamoDB, etc.)..."
cd terraform
~/Downloads/terraform/terraform apply -auto-approve
cd ..
echo "   ✓ Infrastructure deployed"

# Step 6: Verify Lambda function
echo ""
echo "[6/6] Verifying Lambda function..."
aws lambda get-function --function-name $REPO_NAME --region $REGION --no-cli-pager > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Lambda function verified"
else
    echo "   ⚠ Lambda function not found, but continuing..."
fi

echo ""
echo "==================================="
echo "✓ Deployment completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  - Test: aws lambda invoke --function-name $REPO_NAME --region $REGION output.json"
echo "  - Logs: aws logs tail /aws/lambda/$REPO_NAME --follow --region $REGION"
echo ""
