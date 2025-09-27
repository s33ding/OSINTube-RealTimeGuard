# IAM role for EKS pod identity (to be created manually after EKS setup)
# Uncomment after EKS cluster is properly configured

# resource "aws_iam_role" "osintube_pod_role" {
#   name = "osintube-pod-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRoleWithWebIdentity"
#         Effect = "Allow"
#         Principal = {
#           Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}"
#         }
#         Condition = {
#           StringEquals = {
#             "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:default:osintube-sa"
#             "${replace(data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer, "https://", "")}:aud" = "sts.amazonaws.com"
#           }
#         }
#       }
#     ]
#   })
# }

# Data source for account ID
data "aws_caller_identity" "current" {}

# Policy for S3 access
resource "aws_iam_policy" "osintube_s3_policy" {
  name = "osintube-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
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

# Policy for Secrets Manager access
resource "aws_iam_policy" "osintube_secrets_policy" {
  name = "osintube-secrets-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.osintube_secrets.arn
      }
    ]
  })
}

# Policy for Parameter Store access
resource "aws_iam_policy" "osintube_ssm_policy" {
  name = "osintube-ssm-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/osintube/*"
      }
    ]
  })
}

# Policy for Bedrock access with DDoS protection
resource "aws_iam_policy" "osintube_bedrock_policy" {
  name = "osintube-bedrock-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-lite-v1:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/meta.llama3-8b-instruct-v1:0"
        ]
        Condition = {
          "aws:RequestedRegion" = [var.aws_region]
          "IpAddress" = {
            "aws:SourceIp" = ["0.0.0.0/0"]
          }
        }
      }
    ]
  })
}

# Policy for Translate and Comprehend access
resource "aws_iam_policy" "osintube_translate_policy" {
  name = "osintube-translate-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "translate:TranslateText",
          "comprehend:DetectDominantLanguage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policies to role (uncomment after role is created)
# resource "aws_iam_role_policy_attachment" "osintube_s3_attach" {
#   role       = aws_iam_role.osintube_pod_role.name
#   policy_arn = aws_iam_policy.osintube_s3_policy.arn
# }

# resource "aws_iam_role_policy_attachment" "osintube_secrets_attach" {
#   role       = aws_iam_role.osintube_pod_role.name
#   policy_arn = aws_iam_policy.osintube_secrets_policy.arn
# }

# resource "aws_iam_role_policy_attachment" "osintube_ssm_attach" {
#   role       = aws_iam_role.osintube_pod_role.name
#   policy_arn = aws_iam_policy.osintube_ssm_policy.arn
# }

# resource "aws_iam_role_policy_attachment" "osintube_bedrock_attach" {
#   role       = aws_iam_role.osintube_pod_role.name
#   policy_arn = aws_iam_policy.osintube_bedrock_policy.arn
# }

# resource "aws_iam_role_policy_attachment" "osintube_translate_attach" {
#   role       = aws_iam_role.osintube_pod_role.name
#   policy_arn = aws_iam_policy.osintube_translate_policy.arn
# }

# Data sources (uncomment after EKS setup)
# data "aws_caller_identity" "current" {}
# data "aws_eks_cluster" "cluster" {
#   name = var.eks_cluster_name
# }
