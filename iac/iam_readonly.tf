# Read-only role for public data access
resource "aws_iam_role" "osintube_readonly_role" {
  name = "osintube-readonly-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/oidc.eks.sa-east-1.amazonaws.com/id/${var.eks_oidc_provider_id}"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "oidc.eks.sa-east-1.amazonaws.com/id/${var.eks_oidc_provider_id}:sub" = "system:serviceaccount:default:osintube-sa"
            "oidc.eks.sa-east-1.amazonaws.com/id/${var.eks_oidc_provider_id}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Read-only S3 policy for datasets
resource "aws_iam_policy" "osintube_readonly_s3_policy" {
  name        = "osintube-readonly-s3-policy"
  description = "Read-only access to OSINTube S3 datasets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.osintube_data.arn,
          "${aws_s3_bucket.osintube_data.arn}/*"
        ]
      }
    ]
  })
}

# Read-only DynamoDB policy for history
resource "aws_iam_policy" "osintube_readonly_dynamodb_policy" {
  name        = "osintube-readonly-dynamodb-policy"
  description = "Read-only access to OSINTube DynamoDB history"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.osintube_history.arn,
          aws_dynamodb_table.threat_analysis.arn
        ]
      }
    ]
  })
}

# Read-only SSM policy
resource "aws_iam_policy" "osintube_readonly_ssm_policy" {
  name        = "osintube-readonly-ssm-policy"
  description = "Read-only access to OSINTube SSM parameters"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:*:*:parameter/osintube/*"
      }
    ]
  })
}

# Attach policies to read-only role
resource "aws_iam_role_policy_attachment" "readonly_s3_attachment" {
  role       = aws_iam_role.osintube_readonly_role.name
  policy_arn = aws_iam_policy.osintube_readonly_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "readonly_dynamodb_attachment" {
  role       = aws_iam_role.osintube_readonly_role.name
  policy_arn = aws_iam_policy.osintube_readonly_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "readonly_ssm_attachment" {
  role       = aws_iam_role.osintube_readonly_role.name
  policy_arn = aws_iam_policy.osintube_readonly_ssm_policy.arn
}

# Create access keys for read-only role (for programmatic access)
resource "aws_iam_user" "osintube_readonly_user" {
  name = "osintube-readonly-user"
}

resource "aws_iam_user_policy_attachment" "readonly_user_s3" {
  user       = aws_iam_user.osintube_readonly_user.name
  policy_arn = aws_iam_policy.osintube_readonly_s3_policy.arn
}

resource "aws_iam_user_policy_attachment" "readonly_user_dynamodb" {
  user       = aws_iam_user.osintube_readonly_user.name
  policy_arn = aws_iam_policy.osintube_readonly_dynamodb_policy.arn
}

# Store read-only credentials in SSM
resource "aws_iam_access_key" "readonly_access_key" {
  user = aws_iam_user.osintube_readonly_user.name
}

resource "aws_ssm_parameter" "readonly_access_key_id" {
  name  = "/osintube/readonly_access_key_id"
  type  = "String"
  value = aws_iam_access_key.readonly_access_key.id
}

resource "aws_ssm_parameter" "readonly_secret_access_key" {
  name  = "/osintube/readonly_secret_access_key"
  type  = "SecureString"
  value = aws_iam_access_key.readonly_access_key.secret
}
