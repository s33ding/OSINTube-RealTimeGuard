# DynamoDB table for OSINTube search history
resource "aws_dynamodb_table" "osintube_history" {
  name           = "osintube"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "video"

  attribute {
    name = "video"
    type = "S"
  }

  tags = {
    Name = "OSINTube Search History"
  }
}

# DynamoDB table for threat analysis tracking
resource "aws_dynamodb_table" "threat_analysis" {
  name           = "threat_analysis"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "dataset_id"

  attribute {
    name = "dataset_id"
    type = "S"
  }

  tags = {
    Name = "OSINTube Threat Analysis"
  }
}

# DynamoDB table for LLaMA agent analysis
resource "aws_dynamodb_table" "osintube_agent" {
  name           = "osintube-agent"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "analysis_id"

  attribute {
    name = "analysis_id"
    type = "S"
  }

  tags = {
    Name = "OSINTube Agent Analysis"
  }
}

# IAM policy for DynamoDB access
resource "aws_iam_policy" "osintube_dynamodb_policy" {
  name = "osintube-dynamodb-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.osintube_history.arn,
          aws_dynamodb_table.threat_analysis.arn,
          aws_dynamodb_table.osintube_agent.arn
        ]
      }
    ]
  })
}
