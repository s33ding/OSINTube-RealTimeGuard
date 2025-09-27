# Budget alert for Bedrock spending
resource "aws_budgets_budget" "bedrock_budget" {
  name         = "osintube-bedrock-budget"
  budget_type  = "COST"
  limit_amount = "50"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "Service"
    values = ["Amazon Bedrock"]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type          = "ACTUAL"
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
