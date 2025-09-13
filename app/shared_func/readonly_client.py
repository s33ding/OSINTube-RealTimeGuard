import boto3
import os

def get_readonly_clients():
    """Get AWS clients with read-only permissions for public data access"""
    
    # Use read-only credentials from SSM
    ssm = boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    
    try:
        readonly_key_id = ssm.get_parameter(Name='/osintube/readonly_access_key_id')['Parameter']['Value']
        readonly_secret = ssm.get_parameter(Name='/osintube/readonly_secret_access_key', WithDecryption=True)['Parameter']['Value']
        
        # Create read-only clients
        readonly_s3 = boto3.client(
            's3',
            aws_access_key_id=readonly_key_id,
            aws_secret_access_key=readonly_secret,
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        readonly_dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=readonly_key_id,
            aws_secret_access_key=readonly_secret,
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        return readonly_s3, readonly_dynamodb
        
    except Exception as e:
        # Fallback to default credentials if read-only not available
        print(f"Warning: Could not get read-only credentials, using default: {e}")
        return boto3.client('s3'), boto3.client('dynamodb')

def is_public_access():
    """Check if current access should use read-only permissions"""
    # You can implement logic here to determine public vs authenticated access
    # For now, return False to use full permissions for authenticated users
    return False
