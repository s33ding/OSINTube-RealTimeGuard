# IAM policy for Comprehend access
resource "aws_iam_policy" "osintube_comprehend_policy" {
  name = "osintube-comprehend-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "comprehend:DetectSentiment",
          "comprehend:DetectEntities",
          "comprehend:DetectKeyPhrases"
        ]
        Resource = "*"
      }
    ]
  })
}
