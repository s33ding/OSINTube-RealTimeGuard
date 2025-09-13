variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "eks_cluster_name" {
  description = "EKS cluster name in sa-east-1"
  type        = string
}

variable "eks_oidc_provider_id" {
  description = "EKS OIDC provider ID"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for OSINTube data"
  type        = string
  default     = "s33ding-osintube"
}

variable "youtube_api_key" {
  description = "YouTube Data API key"
  type        = string
  sensitive   = true
}

variable "github_repo_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/s33ding/OSINTube-RealTimeGuard.git"
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret"
  type        = string
  default     = ""
  sensitive   = true
}
