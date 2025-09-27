# ECR Repository
resource "aws_ecr_repository" "osintube" {
  name                 = "osintube"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Parameter Store values for CodeBuild
resource "aws_ssm_parameter" "ecr_repository_uri" {
  name  = "/osintube/ecr_repository_uri"
  type  = "String"
  value = aws_ecr_repository.osintube.repository_url
}

# Use existing s33ding GitHub connection
data "aws_codestarconnections_connection" "s33ding" {
  name = "s33ding"
}

# CodeBuild Service Role
resource "aws_iam_role" "codebuild_role" {
  name = "osintube-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "codebuild_policy" {
  role = aws_iam_role.codebuild_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:*:*:parameter/osintube/*"
      },
      {
        Effect = "Allow"
        Action = [
          "codestar-connections:UseConnection"
        ]
        Resource = data.aws_codestarconnections_connection.s33ding.arn
      }
    ]
  })
}

# CodeBuild Project
resource "aws_codebuild_project" "osintube" {
  name          = "osintube-build"
  description   = "Build and push OSINTube Docker image"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_LARGE"
    image                      = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = data.aws_caller_identity.current.account_id
    }
  }

  source {
    type            = "GITHUB"
    location        = var.github_repo_url
    git_clone_depth = 1
    buildspec       = "buildspec.yml"
    
    auth {
      type     = "CODECONNECTIONS"
      resource = data.aws_codestarconnections_connection.s33ding.arn
    }
  }

  source_version = "main"
}

# CodeBuild Webhook for automatic triggering
resource "aws_codebuild_webhook" "osintube" {
  project_name = aws_codebuild_project.osintube.name
  build_type   = "BUILD"

  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "refs/heads/main"
    }
  }
}
