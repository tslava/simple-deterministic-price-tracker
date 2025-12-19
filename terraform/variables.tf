variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "my-price-tracker"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "service_name" {
  description = "Service name for Lambda function"
  type        = string
  default     = "price-tracker"
}

variable "product_url" {
  description = "URL of the product to track"
  type        = string
}

variable "price_selector" {
  description = "CSS selector for the price element"
  type        = string
}

variable "telegram_bot_token" {
  description = "Telegram bot API token"
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID for notifications"
  type        = string
  sensitive   = true
}

variable "schedule_expression" {
  description = "Cron expression for EventBridge Scheduler"
  type        = string
  default     = "cron(0 17 * * ? *)"  # Daily at 10:00 UTC
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300  # 5 minutes
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 2048  # 2 GB
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 7
}
