# Cognito User Pool
resource "aws_cognito_user_pool" "osintube_pool" {
  name = "osintube-users"

  # Only allow email login
  username_attributes = ["email"]
  
  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # Email configuration
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Auto-verified attributes
  auto_verified_attributes = ["email"]

  tags = {
    Name = "OSINTube User Pool"
  }
}

# Google Identity Provider
resource "aws_cognito_identity_provider" "google" {
  user_pool_id  = aws_cognito_user_pool.osintube_pool.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    client_id        = var.google_client_id
    client_secret    = var.google_client_secret
    authorize_scopes = "email openid profile"
  }

  attribute_mapping = {
    email    = "email"
    username = "sub"
    name     = "name"
  }
}

# Cognito User Pool Client
resource "aws_cognito_user_pool_client" "osintube_client" {
  name         = "osintube-client"
  user_pool_id = aws_cognito_user_pool.osintube_pool.id

  generate_secret = false
  
  # OAuth settings
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls                        = ["https://osintube.dataiesb.com/callback", "https://osintube.dataiesb.com"]
  logout_urls                          = ["https://osintube.dataiesb.com"]
  
  # Use Google as identity provider
  supported_identity_providers = ["Google"]
  
  # Enable hosted UI
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  depends_on = [aws_cognito_identity_provider.google]
}

# Cognito User Pool Domain
resource "aws_cognito_user_pool_domain" "osintube_domain" {
  domain       = "osintube-${random_string.suffix.result}"
  user_pool_id = aws_cognito_user_pool.osintube_pool.id
}

# Cognito Identity Pool
resource "aws_cognito_identity_pool" "osintube_identity_pool" {
  identity_pool_name               = "osintube_identity_pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.osintube_client.id
    provider_name           = aws_cognito_user_pool.osintube_pool.endpoint
    server_side_token_check = false
  }
}

# IAM role for authenticated users with full access
resource "aws_iam_role" "cognito_authenticated" {
  name = "Cognito_osintube_authenticated_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.osintube_identity_pool.id
          }
          "ForAnyValue:StringLike" = {
            "cognito-identity.amazonaws.com:amr" = "authenticated"
          }
        }
      }
    ]
  })
}

# Policy for full access to OSINTube resources
resource "aws_iam_role_policy" "cognito_authenticated_policy" {
  name = "cognito_authenticated_policy"
  role = aws_iam_role.cognito_authenticated.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:*"
        ]
        Resource = aws_dynamodb_table.osintube_history.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          aws_s3_bucket.osintube_data.arn,
          "${aws_s3_bucket.osintube_data.arn}/*"
        ]
      }
    ]
  })
}

# Attach the role to the identity pool
resource "aws_cognito_identity_pool_roles_attachment" "osintube_roles" {
  identity_pool_id = aws_cognito_identity_pool.osintube_identity_pool.id

  roles = {
    "authenticated" = aws_iam_role.cognito_authenticated.arn
  }
}

# Store Identity Pool ID in Parameter Store
resource "aws_ssm_parameter" "cognito_identity_pool_id" {
  name  = "/osintube/cognito_identity_pool_id"
  type  = "String"
  value = aws_cognito_identity_pool.osintube_identity_pool.id
}

# Store Cognito details in Parameter Store
resource "aws_ssm_parameter" "cognito_user_pool_id" {
  name  = "/osintube/cognito_user_pool_id"
  type  = "String"
  value = aws_cognito_user_pool.osintube_pool.id
}

resource "aws_ssm_parameter" "cognito_client_id" {
  name  = "/osintube/cognito_client_id"
  type  = "String"
  value = aws_cognito_user_pool_client.osintube_client.id
}

resource "aws_ssm_parameter" "cognito_domain" {
  name  = "/osintube/cognito_domain"
  type  = "String"
  value = aws_cognito_user_pool_domain.osintube_domain.domain
}
