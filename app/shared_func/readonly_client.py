import boto3
import os
import streamlit as st
from shared_func.boto3_session import create_boto3_session

def get_clients():
    """Get appropriate clients based on authentication status using session"""
    
    try:
        session = create_boto3_session()
        s3_client = session.client('s3', region_name='us-east-1')
        dynamodb_client = session.client('dynamodb', region_name='us-east-1')
        
        return s3_client, dynamodb_client
        
    except Exception as e:
        st.error(f"❌ Could not initialize AWS clients: {e}")
        return None, None

# Keep backward compatibility
def get_readonly_clients():
    """Get AWS clients with read-only permissions using stored credentials"""
    return get_clients()

def get_authenticated_clients():
    """Get AWS clients with full permissions for authenticated users"""
    return get_clients()
