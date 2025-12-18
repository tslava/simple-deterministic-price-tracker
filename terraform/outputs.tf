output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.price_tracker.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.price_tracker.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.price_history.name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.price_tracker.repository_url
}

output "scheduler_name" {
  description = "Name of the EventBridge Scheduler"
  value       = aws_scheduler_schedule.price_check.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch Logs group name"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}
