# Budget alert for Bedrock spending
resource "aws_budgets_budget" "bedrock_budget" {
  name         = "osintube-bedrock-budget"
  budget_type  = "COST"
  limit_amount = "50"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon Bedrock"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }
}

# CloudWatch alarm for high request rate
resource "aws_cloudwatch_metric_alarm" "bedrock_ddos_alarm" {
  alarm_name          = "osintube-bedrock-ddos-protection"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Invocations"
  namespace           = "AWS/Bedrock"
  period              = "60"
  statistic           = "Sum"
  threshold           = "50"
  alarm_description   = "DDoS protection - too many Bedrock requests"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ModelId = "meta.llama3-8b-instruct-v1:0"
  }
}

# Lambda function for request throttling
resource "aws_lambda_function" "bedrock_throttle" {
  filename         = "throttle.zip"
  function_name    = "osintube-bedrock-throttle"
  role            = aws_iam_role.lambda_throttle_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      MAX_REQUESTS_PER_MINUTE = "30"
    }
  }
}

# IAM role for throttle Lambda
resource "aws_iam_role" "lambda_throttle_role" {
  name = "osintube-lambda-throttle-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_throttle_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
