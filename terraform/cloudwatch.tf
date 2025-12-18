resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.service_name}"
  retention_in_days = var.log_retention_days

  # Free tier: 5GB ingestion, 5GB storage
  # Estimated: ~10-20MB/month with INFO level logging

  tags = {
    Name = "Price Tracker Lambda Logs"
  }
}
