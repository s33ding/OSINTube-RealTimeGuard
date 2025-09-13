import boto3
import os
import streamlit as st

def get_readonly_clients():
    """Get AWS clients with read-only permissions using pod identity"""
    
    try:
        # Pod identity will automatically provide read-only credentials
        # The pod's service account should be associated with a read-only IAM role
        readonly_s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        readonly_dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        
        return readonly_s3, readonly_dynamodb
        
    except Exception as e:
        st.error(f"❌ Could not initialize read-only clients: {e}")
        return None, None

def get_authenticated_clients():
    """Get AWS clients with full permissions for authenticated users via Cognito"""
    
    # Check if user is authenticated via Cognito
    if 'cognito_tokens' not in st.session_state:
        return None, None
    
    try:
        # Use Cognito identity pool to get temporary credentials with elevated permissions
        cognito_identity = boto3.client('cognito-identity', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        
        # Get identity ID using the ID token
        identity_response = cognito_identity.get_id(
            IdentityPoolId=os.environ.get('COGNITO_IDENTITY_POOL_ID'),
            Logins={
                f'cognito-idp.{os.environ.get("AWS_REGION", "us-east-1")}.amazonaws.com/{os.environ.get("COGNITO_USER_POOL_ID")}': st.session_state.cognito_tokens['IdToken']
            }
        )
        
        # Get temporary credentials with elevated permissions
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_response['IdentityId'],
            Logins={
                f'cognito-idp.{os.environ.get("AWS_REGION", "us-east-1")}.amazonaws.com/{os.environ.get("COGNITO_USER_POOL_ID")}': st.session_state.cognito_tokens['IdToken']
            }
        )
        
        credentials = credentials_response['Credentials']
        
        # Create authenticated clients with full permissions
        auth_s3 = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        auth_dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        return auth_s3, auth_dynamodb
        
    except Exception as e:
        st.warning(f"⚠️ Could not get authenticated credentials, using read-only: {e}")
        return None, None

def get_clients():
    """Get appropriate clients based on authentication status"""
    
    # If user is authenticated, try to get elevated permissions
    if 'cognito_tokens' in st.session_state and st.session_state.get('authenticated', False):
        auth_clients = get_authenticated_clients()
        if auth_clients[0] is not None:
            st.info("🔓 Using authenticated access with full permissions")
            return auth_clients
    
    # Use pod identity with read-only permissions
    st.info("👁️ Using read-only access via pod identity")
    return get_readonly_clients()
