import os
import boto3
import json

# Check if running locally
LOCAL_MODE = os.getenv('LOCAL_MODE', 'false').lower() == 'true'

if not LOCAL_MODE:
    # Production mode - use AWS services
    ssm = boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    secrets_client = boto3.client('secretsmanager', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

    def get_parameter(name):
        response = ssm.get_parameter(Name=name)
        return response['Parameter']['Value']

    def get_secrets():
        secret_name = os.environ.get('SECRET_NAME', 'osintube-secrets')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])

    secrets = get_secrets()
    youtube_api_key = secrets['youtube_api_key']
    bucket_name = get_parameter('/osintube/s3_bucket_name')
    cognito_user_pool_id = get_parameter('/osintube/cognito_user_pool_id')
    cognito_client_id = get_parameter('/osintube/cognito_client_id')
    cognito_domain = get_parameter('/osintube/cognito_domain')
else:
    # Local mode - use environment variables or defaults
    def get_parameter(name):
        param_map = {
            '/osintube/s3_bucket_name': os.getenv('LOCAL_S3_BUCKET', 'osintube-local-bucket'),
            '/osintube/cognito_user_pool_id': os.getenv('LOCAL_COGNITO_USER_POOL_ID', 'us-east-1_XXXXXXXXX'),
            '/osintube/cognito_client_id': os.getenv('LOCAL_COGNITO_CLIENT_ID', 'your-local-client-id'),
            '/osintube/cognito_domain': os.getenv('LOCAL_COGNITO_DOMAIN', 'your-local-domain')
        }
        return param_map.get(name, 'local-mock-value')

    youtube_api_key = os.getenv('LOCAL_YOUTUBE_API_KEY', 'your-local-youtube-api-key')
    bucket_name = get_parameter('/osintube/s3_bucket_name')
    cognito_user_pool_id = get_parameter('/osintube/cognito_user_pool_id')
    cognito_client_id = get_parameter('/osintube/cognito_client_id')
    cognito_domain = get_parameter('/osintube/cognito_domain')

# Common configuration values
comments_maxResult = 80
search_limit = 5
bedrock_model_id = "us.meta.llama4-scout-17b-instruct-v1:0"
default_file_name = "data.pickle"
output_path = f"output/{default_file_name}"
delete_file = False
img_path = "media/osintube.webp"

readme = """
OSINTube-RealTimeGuard is a real-time threat detection system for YouTube content, ensuring online safety by identifying threats and suspicious activities through continuous monitoring and analysis. It leverages the YouTube Data API v3 to search for videos, AWS Translate for multilingual support, Amazon S3 for data storage, NLP for text tokenization, Amazon Bedrock for sentiment analysis, Streamlit for the backend interface, and Docker for easy deployment.
"""

