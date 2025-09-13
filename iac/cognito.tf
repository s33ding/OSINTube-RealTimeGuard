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
  callback_urls                        = ["http://localhost:8501/callback", "http://localhost:8501"]
  logout_urls                          = ["http://localhost:8501"]
  
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
