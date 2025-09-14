import boto3
import os

def get_base_url():
    try:
        ssm = boto3.client('ssm', region_name='us-east-1')
        response = ssm.get_parameter(Name='/osintube/base_url')
        return response['Parameter']['Value']
    except:
        return "https://app.dataiesb.com/osintube"
