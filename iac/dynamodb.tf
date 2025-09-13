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
        Resource = aws_dynamodb_table.osintube_history.arn
      }
    ]
  })
}
