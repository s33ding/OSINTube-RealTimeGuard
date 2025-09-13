terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Parameter Store for non-sensitive configuration
resource "aws_ssm_parameter" "container_name" {
  name  = "/osintube/container_name"
  type  = "String"
  value = "ytb"
}

resource "aws_ssm_parameter" "image_name" {
  name  = "/osintube/image_name"
  type  = "String"
  value = "img-ytb"
}

resource "aws_ssm_parameter" "container_port" {
  name  = "/osintube/container_port"
  type  = "String"
  value = "8501"
}

# Secrets Manager for sensitive data
resource "aws_secretsmanager_secret" "osintube_secrets" {
  name = "osintube-secrets"
}

resource "aws_secretsmanager_secret_version" "osintube_secrets" {
  secret_id = aws_secretsmanager_secret.osintube_secrets.id
  secret_string = jsonencode({
    youtube_api_key = var.youtube_api_key
  })
}

# ECR repository for container images
# resource "aws_ecr_repository" "osintube" {
#   name = "osintube"
# }

# Parameter for ECR repository URL
# resource "aws_ssm_parameter" "ecr_repository_url" {
#   name  = "/osintube/ecr_repository_url"
#   type  = "String"
#   value = aws_ecr_repository.osintube.repository_url
# }

# S3 bucket for data storage
resource "aws_s3_bucket" "osintube_data" {
  bucket = "${var.s3_bucket_name}-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "osintube_data" {
  bucket = aws_s3_bucket.osintube_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Parameter for S3 bucket name
resource "aws_ssm_parameter" "s3_bucket_name" {
  name  = "/osintube/s3_bucket_name"
  type  = "String"
  value = aws_s3_bucket.osintube_data.bucket
}
