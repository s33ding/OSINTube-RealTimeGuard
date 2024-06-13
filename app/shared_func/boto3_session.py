import boto3
import json
import os
import config

def create_boto3_session(aws_key=config.aws_key, aws_secret=config.aws_secret):
    """
    Creates a new Boto3 session using AWS credentials stored in a JSON file.

    Parameters:
    - json_file_path (str): The path to the JSON file containing the AWS credentials.

    Returns:
    - Boto3 session object.
    """
    return boto3.Session(
        region_name='us-east-1',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret
        )
