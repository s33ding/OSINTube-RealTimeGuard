import boto3
import os

def create_boto3_session():
    """
    Creates a new Boto3 session using pod identity (no explicit credentials needed).
    
    Returns:
    - Boto3 session object.
    """
    return boto3.Session(
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
