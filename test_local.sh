#!/bin/bash

# Stop and remove existing container
docker stop osintube-test 2>/dev/null || true
docker rm osintube-test 2>/dev/null || true

# Get STS credentials like deploy_local.py
python3 -c "
import boto3
import os

sts = boto3.client('sts')
role_arn = 'arn:aws:iam::248189947068:role/osintube-readonly-role'

credentials = sts.assume_role(
    RoleArn=role_arn,
    RoleSessionName='osintube-local-test'
)['Credentials']

print(f'export AWS_ACCESS_KEY_ID={credentials[\"AccessKeyId\"]}')
print(f'export AWS_SECRET_ACCESS_KEY={credentials[\"SecretAccessKey\"]}')
print(f'export AWS_SESSION_TOKEN={credentials[\"SessionToken\"]}')
" > /tmp/aws_creds.sh

source /tmp/aws_creds.sh

# Build and run locally with AWS credentials
docker build -f docker-image/Dockerfile -t osintube-test .
docker run --name osintube-test -p 8501:8501 \
  -v $(pwd)/app/:/app/ \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN" \
  -e AWS_DEFAULT_REGION=us-east-1 \
  osintube-test
