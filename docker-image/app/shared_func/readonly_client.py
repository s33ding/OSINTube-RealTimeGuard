import boto3
import os
import streamlit as st

def get_readonly_clients():
    """Get AWS clients with read-only permissions using stored credentials"""
    
    try:
        # Get read-only credentials from SSM
        ssm = boto3.client('ssm', region_name='us-east-1')
        
        access_key_response = ssm.get_parameter(Name='/osintube/readonly_access_key_id')
        secret_key_response = ssm.get_parameter(Name='/osintube/readonly_secret_access_key', WithDecryption=True)
        
        access_key = access_key_response['Parameter']['Value']
        secret_key = secret_key_response['Parameter']['Value']
        
        # Create read-only clients
        readonly_s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        readonly_dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        return readonly_s3, readonly_dynamodb
        
    except Exception as e:
        st.error(f"❌ Could not initialize read-only clients: {e}")
        return None, None

def get_authenticated_clients():
    """Get AWS clients with full permissions for authenticated users"""
    
    try:
        # Use default credentials for authenticated users
        auth_s3 = boto3.client('s3', region_name='us-east-1')
        auth_dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        return auth_s3, auth_dynamodb
        
    except Exception as e:
        st.warning(f"⚠️ Could not get authenticated credentials: {e}")
        return None, None

def get_clients():
    """Get appropriate clients based on authentication status"""
    
    # Check if user is authenticated
    if hasattr(st.session_state, 'authenticated') and st.session_state.authenticated:
        return get_authenticated_clients()
    else:
        return get_readonly_clients()
