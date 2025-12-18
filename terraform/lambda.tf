resource "aws_lambda_function" "price_tracker" {
  function_name = var.service_name
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.price_tracker.repository_url}:latest"

  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory
  architectures = ["arm64"]  # Match Docker image architecture (Apple Silicon)

  environment {
    variables = {
      PRODUCT_URL               = var.product_url
      PRICE_SELECTOR            = var.price_selector
      DYNAMODB_TABLE            = aws_dynamodb_table.price_history.name
      SSM_PREFIX                = "/${var.project_name}"
      TELEGRAM_BOT_TOKEN_PARAM  = aws_ssm_parameter.telegram_bot_token.name
      TELEGRAM_CHAT_ID_PARAM    = aws_ssm_parameter.telegram_chat_id.name
      PLAYWRIGHT_BROWSERS_PATH  = "/opt/playwright"
    }
  }

  # No VPC configuration (direct internet access, no NAT Gateway cost)

  # Free tier: 1M requests/month, 400K GB-seconds compute
  # Daily invocation = 30 requests/month, ~150-300 GB-seconds/month
  # Well within free tier limits

  tags = {
    Name = "Price Tracker"
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs
  ]
}
