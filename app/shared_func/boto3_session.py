import boto3
import os
import streamlit as st
import config

def create_boto3_session():
    """
    Creates a new Boto3 session using Cognito credentials if authenticated,
    otherwise uses pod identity.
    
    Returns:
    - Boto3 session object.
    """
    # Check if user is authenticated and has id_token
    if st.session_state.get('authenticated') and st.session_state.get('id_token'):
        try:
            # Use Cognito Identity to get AWS credentials
            cognito_identity = boto3.client('cognito-identity', region_name='us-east-1')
            
            # Get identity ID
            identity_response = cognito_identity.get_id(
                IdentityPoolId=config.get_parameter('/osintube/cognito_identity_pool_id'),
                Logins={
                    f'cognito-idp.us-east-1.amazonaws.com/{config.get_parameter("/osintube/cognito_user_pool_id")}': st.session_state['id_token']
                }
            )
            
            identity_id = identity_response['IdentityId']
            
            # Get credentials for the identity
            credentials_response = cognito_identity.get_credentials_for_identity(
                IdentityId=identity_id,
                Logins={
                    f'cognito-idp.us-east-1.amazonaws.com/{config.get_parameter("/osintube/cognito_user_pool_id")}': st.session_state['id_token']
                }
            )
            
            credentials = credentials_response['Credentials']
            
            # Create session with Cognito credentials
            return boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
            
        except Exception as e:
            st.error(f"Failed to get Cognito credentials: {e}")
            # Fall back to pod identity
            pass
    
    # Use pod identity (EKS service account)
    return boto3.Session(
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
