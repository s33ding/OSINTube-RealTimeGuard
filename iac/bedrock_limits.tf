# Advanced Bedrock rate limiting policy
resource "aws_iam_policy" "osintube_bedrock_rate_limit" {
  name = "osintube-bedrock-rate-limit"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "BedrockInvokeWithLimits"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-lite-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/meta.llama3-8b-instruct-v1:0"
        ]
        Condition = {
          "aws:RequestedRegion" = [var.aws_region]
          "StringEquals" = {
            "bedrock:modelId" = [
              "amazon.nova-lite-v1:0",
              "meta.llama3-8b-instruct-v1:0"
            ]
          }
        }
      },
      {
        Sid = "DenyHighCostModels"
        Effect = "Deny"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:*::foundation-model/*"
        Condition = {
          "StringNotEquals" = {
            "bedrock:modelId" = [
              "amazon.nova-lite-v1:0",
              "meta.llama3-8b-instruct-v1:0"
            ]
          }
        }
      }
    ]
  })
}

# CloudWatch alarm for monitoring Bedrock usage
resource "aws_cloudwatch_metric_alarm" "bedrock_usage_alarm" {
  alarm_name          = "osintube-bedrock-high-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Invocations"
  namespace           = "AWS/Bedrock"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "This metric monitors bedrock invocations"
  alarm_actions       = []

  dimensions = {
    ModelId = "meta.llama3-8b-instruct-v1:0"
  }
}
