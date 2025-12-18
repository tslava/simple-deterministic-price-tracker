# Price Tracker - AWS Lambda (Free Tier)

A serverless price tracker that runs daily on AWS Lambda, scrapes product prices using Playwright, stores history in DynamoDB, and sends notifications via Telegram - all within AWS free tier limits.

## Architecture

- **Lambda Function**: Python 3.12 container image with Playwright
- **Database**: DynamoDB (on-demand, always-free 25GB)
- **Scheduling**: EventBridge Scheduler (daily trigger)
- **Configuration**: SSM Parameter Store (free)
- **Notifications**: Telegram Bot API
- **Infrastructure**: Terraform

## Cost

**~$0-$0.20/month** (essentially free with AWS free tier)

## Prerequisites

- AWS Account
- AWS CLI configured
- Docker installed
- Terraform installed
- Python 3.12
- Telegram account

## Quick Start

### 1. Create Telegram Bot

Follow instructions in `scripts/setup_telegram_bot.md`

### 2. Clone and Configure

```bash
cd price_tracker

# Create terraform variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your values
```

### 3. Build and Push Docker Image

```bash
# Build Lambda container
docker build -t price-tracker .

# Authenticate to ECR
aws ecr get-login-password --region eu-west-3 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-3.amazonaws.com

# Create ECR repository (first time only)
aws ecr create-repository --repository-name price-tracker --region eu-west-3

# Tag and push
docker tag price-tracker:latest <account-id>.dkr.ecr.eu-west-3.amazonaws.com/price-tracker:latest
docker push <account-id>.dkr.ecr.eu-west-3.amazonaws.com/price-tracker:latest
```

### 4. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 5. Test

```bash
# Invoke Lambda manually
aws lambda invoke \
  --function-name price-tracker \
  --region eu-west-3 \
  output.json

# Check logs
aws logs tail /aws/lambda/price-tracker --follow
```

## Configuration

### Product Tracking

Update these in `terraform/terraform.tfvars`:

- `product_url`: URL of the product page
- `price_selector`: CSS selector for the price element

Example:
```hcl
product_url = "https://www.amazon.com/dp/B08N5WRWNW"
price_selector = ".a-price-whole"
```

### Schedule

Default: Daily at 10:00 UTC

Change in `terraform/scheduler.tf`:
```hcl
schedule_expression = "cron(0 17 * * ? *)"
```

## Monitoring

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/price-tracker --follow
```

### DynamoDB Table

View price history in AWS Console: DynamoDB → Tables → price-history

### Lambda Metrics

AWS Console: Lambda → Functions → price-tracker → Monitoring

## Troubleshooting

### Lambda fails with timeout

Increase timeout in `terraform/lambda.tf`:
```hcl
timeout = 300  # seconds
```

### Price selector not working

1. Open the product URL in a browser
2. Inspect the price element
3. Copy the CSS selector
4. Update `price_selector` in `terraform/terraform.tfvars`
5. Re-apply Terraform

### No Telegram notifications

1. Verify bot token: Test with `https://api.telegram.org/bot<TOKEN>/getMe`
2. Verify chat ID: Send message to bot, then check `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Check Lambda logs for errors

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Test with mocked AWS
pip install moto
python -c "from src.lambda_handler import lambda_handler; lambda_handler({}, None)"
```

### Docker Testing

```bash
docker build -t price-tracker .

# Test with Lambda RIE
docker run -p 9000:8080 \
  -e PRODUCT_URL="https://example.com" \
  -e PRICE_SELECTOR=".price" \
  price-tracker

curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

## Free Tier Limits

- Lambda: 1M requests/month, 400K GB-seconds
- EventBridge: 14M invocations/month
- DynamoDB: 25GB storage, 25 RCU/WCU
- CloudWatch: 5GB logs
- ECR: 500MB storage

Daily price check uses:
- ~30 Lambda requests/month
- ~300 GB-seconds compute
- <1MB DynamoDB storage/day
- ~20MB logs/month

All well within free tier!

## License

MIT
