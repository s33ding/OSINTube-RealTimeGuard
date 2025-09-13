output "secret_arn" {
  description = "ARN of the secrets manager secret"
  value       = aws_secretsmanager_secret.osintube_secrets.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.osintube_data.bucket
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.osintube.repository_url
}

output "github_connection_arn" {
  description = "ARN of the GitHub CodeConnections connection"
  value       = aws_codestarconnections_connection.github.arn
}

# output "pod_role_arn" {
#   description = "ARN of the pod IAM role"
#   value       = aws_iam_role.osintube_pod_role.arn
# }
