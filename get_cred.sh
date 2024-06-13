#!/bin/bash

# Define the secret name and region
SECRET_NAME="s33ding"
REGION="us-east-1"

# Fetch the secret value using AWS CLI
SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id $SECRET_NAME --region $REGION --query 'SecretString' --output text)

# Parse the JSON and extract the values
GCP_VALUE=$(echo $SECRET_JSON | jq -r '.gcp')
OPENAI_VALUE=$(echo $SECRET_JSON | jq -r '.openai')

# Export the values as environment variables
export GCP_SECRET="$GCP_VALUE"
export OPENAI_SECRET="$OPENAI_VALUE"
