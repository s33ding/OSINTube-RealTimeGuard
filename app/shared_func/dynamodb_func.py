import boto3
from datetime import datetime
import pytz
import re
import hashlib
from shared_func.boto3_session import create_boto3_session

def get_dynamodb_client():
    session = create_boto3_session()
    return session.client('dynamodb', region_name='us-east-1')

def normalize_title(title):
    """Normalize title for consistent PK generation"""
    if not title:
        return "unknown"
    # Remove special chars, convert to lowercase, replace spaces with underscores
    normalized = re.sub(r'[^\w\s-]', '', title.lower())
    normalized = re.sub(r'\s+', '_', normalized.strip())
    return normalized[:50]  # Limit length

def extract_youtube_links(video_query):
    """Extract YouTube video links from query"""
    links = []
    
    # Extract video ID from various YouTube URL formats
    video_id_patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]
    
    for pattern in video_id_patterns:
        matches = re.findall(pattern, video_query)
        for match in matches:
            links.append(f"https://www.youtube.com/watch?v={match}")
    
    return links if links else [video_query]

def log_search_to_dynamodb(video_query, s3_key, max_comments=10, max_videos=1, comments_found=0):
    """
    Log search query to DynamoDB with normalized PK and extracted links
    """
    dynamodb = get_dynamodb_client()
    
    # Get current timestamp
    sp_tz = pytz.timezone('America/Sao_Paulo')
    timestamp = datetime.now(sp_tz).isoformat()
    
    # Create normalized PK: normalized_title + timestamp hash
    normalized_title = normalize_title(video_query)
    timestamp_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    pk = f"{normalized_title}_{timestamp_hash}"
    
    # Extract YouTube links
    links = extract_youtube_links(video_query)
    
    # Create full S3 path
    bucket_name = "s33ding-osintube-w7p7627g"  # From config
    s3_full_path = f"s3://{bucket_name}/{s3_key}"
    
    # Additional metadata
    search_date = datetime.now(sp_tz).strftime('%Y-%m-%d')
    search_time = datetime.now(sp_tz).strftime('%H:%M:%S')
    
    try:
        response = dynamodb.put_item(
            TableName='osintube',
            Item={
                'video': {'S': pk},  # Changed from 'pk' to 'video' to match table schema
                'video_query': {'S': video_query},
                's3': {'S': s3_key},
                's3_full_path': {'S': s3_full_path},
                'timestamp': {'S': timestamp},
                'search_date': {'S': search_date},
                'search_time': {'S': search_time},
                'max_comments': {'N': str(max_comments)},
                'max_videos': {'N': str(max_videos)},
                'comments_found': {'N': str(comments_found)},
                'bucket_name': {'S': bucket_name},
                'status': {'S': 'completed'}
            }
        )
        return True
    except Exception as e:
        print(f"DynamoDB error: {e}")
        return False
