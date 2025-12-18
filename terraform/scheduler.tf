resource "aws_scheduler_schedule" "price_check" {
  name       = "${var.service_name}-daily-check"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.schedule_expression

  target {
    arn      = aws_lambda_function.price_tracker.arn
    role_arn = aws_iam_role.eventbridge_scheduler.arn

    retry_policy {
      maximum_retry_attempts       = 3
      maximum_event_age_in_seconds = 3600
    }
  }

  # Free tier: 14M invocations/month
  # Daily schedule = 30 invocations/month (well within limits)

  depends_on = [
    aws_lambda_function.price_tracker,
    aws_iam_role.eventbridge_scheduler
  ]
}

# Permission for EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.price_tracker.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.price_check.arn
}
