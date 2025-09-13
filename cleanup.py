#!/usr/bin/env python3
import boto3
import sys

def cleanup_resources():
    """Clean S3 bucket and empty DynamoDB table"""
    
    # Get resource names from SSM
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    try:
        bucket_name = ssm.get_parameter(Name='/osintube/s3_bucket_name')['Parameter']['Value']
        print(f"Found S3 bucket: {bucket_name}")
    except Exception as e:
        print(f"Error getting S3 bucket name: {e}")
        return False
    
    # Clean S3 bucket
    try:
        s3 = boto3.resource('s3', region_name='us-east-1')
        bucket = s3.Bucket(bucket_name)
        
        # Delete all objects
        objects = list(bucket.objects.all())
        if objects:
            bucket.delete_objects(Delete={'Objects': [{'Key': obj.key} for obj in objects]})
            print(f"Deleted {len(objects)} objects from S3 bucket")
        else:
            print("S3 bucket is already empty")
            
    except Exception as e:
        print(f"Error cleaning S3 bucket: {e}")
        return False
    
    # Clean DynamoDB table
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('osintube')
        
        # Scan and delete all items
        response = table.scan()
        items = response.get('Items', [])
        
        if items:
            with table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={'id': item['id']})
            print(f"Deleted {len(items)} items from DynamoDB table")
        else:
            print("DynamoDB table is already empty")
            
    except Exception as e:
        print(f"Error cleaning DynamoDB table: {e}")
        return False
    
    print("✅ Cleanup completed successfully")
    return True

if __name__ == "__main__":
    success = cleanup_resources()
    sys.exit(0 if success else 1)
