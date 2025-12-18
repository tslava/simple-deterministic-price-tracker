# Lambda execution role
resource "aws_iam_role" "lambda_exec" {
  name = "${var.service_name}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "Price Tracker Lambda Execution Role"
  }
}

# Lambda policy: DynamoDB, SSM, CloudWatch Logs
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.service_name}-lambda-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.price_history.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:${var.region}:*:parameter/${var.project_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:*:log-group:/aws/lambda/${var.service_name}:*"
      }
    ]
  })
}

# EventBridge Scheduler role
resource "aws_iam_role" "eventbridge_scheduler" {
  name = "${var.service_name}-eventbridge-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "Price Tracker EventBridge Scheduler Role"
  }
}

# EventBridge policy: Invoke Lambda
resource "aws_iam_role_policy" "eventbridge_policy" {
  name = "${var.service_name}-eventbridge-policy"
  role = aws_iam_role.eventbridge_scheduler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.price_tracker.arn
    }]
  })
}
