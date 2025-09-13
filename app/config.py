import os
import boto3
import json

# Initialize AWS clients
ssm = boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
secrets_client = boto3.client('secretsmanager', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Get configuration from Parameter Store
def get_parameter(name):
    response = ssm.get_parameter(Name=name)
    return response['Parameter']['Value']

# Get secrets from Secrets Manager
def get_secrets():
    secret_name = os.environ.get('SECRET_NAME', 'osintube-secrets')
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secrets()

# Configuration values
comments_maxResult = 80
youtube_api_key = secrets['youtube_api_key']
search_limit = 5
bucket_name = get_parameter('/osintube/s3_bucket_name')
bedrock_model_id = "us.meta.llama4-scout-17b-instruct-v1:0"
cognito_user_pool_id = get_parameter('/osintube/cognito_user_pool_id')
cognito_client_id = get_parameter('/osintube/cognito_client_id')
cognito_domain = get_parameter('/osintube/cognito_domain')
default_file_name = "data.pickle"
output_path = f"output/{default_file_name}"
delete_file = False
img_path = "media/osintube.webp"

readme = """
OSINTube-RealTimeGuard is a real-time threat detection system for YouTube content, ensuring online safety by identifying threats and suspicious activities through continuous monitoring and analysis. It leverages the YouTube Data API v3 to search for videos, AWS Translate for multilingual support, Amazon S3 for data storage, NLP for text tokenization, Amazon Bedrock for sentiment analysis, Streamlit for the backend interface, and Docker for easy deployment.
"""

