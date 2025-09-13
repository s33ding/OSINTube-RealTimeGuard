import boto3
import pandas as pd
from datetime import datetime

def get_dynamodb_client():
    return boto3.client('dynamodb', region_name='us-east-1')

def get_search_history():
    """Get all search history from DynamoDB"""
    dynamodb = get_dynamodb_client()
    
    try:
        response = dynamodb.scan(TableName='osintube')
        
        # Convert DynamoDB format to DataFrame
        items = []
        for item in response['Items']:
            record = {
                'Search Query': item.get('video', {}).get('S', ''),
                'S3 Path': item.get('s3', {}).get('S', ''),
                'Timestamp': item.get('timestamp', {}).get('S', ''),
                'Max Comments': int(item.get('max_comments', {}).get('N', '0')),
                'Max Videos': int(item.get('max_videos', {}).get('N', '0')),
                'Video Links': extract_video_links(item.get('s3', {}).get('S', ''))
            }
            items.append(record)
        
        df = pd.DataFrame(items)
        
        # Sort by timestamp (newest first)
        if not df.empty:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values('Timestamp', ascending=False)
            df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return df
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        return pd.DataFrame()

def extract_video_links(s3_path):
    """Extract video links from S3 data (placeholder - would need to read S3 file)"""
    # This would typically read the S3 file and extract video links
    # For now, return placeholder
    return "Links available in S3 data"

def get_history_stats():
    """Get statistics about search history"""
    df = get_search_history()
    
    if df.empty:
        return {
            'total_searches': 0,
            'total_comments': 0,
            'total_videos': 0,
            'last_search': 'Never'
        }
    
    return {
        'total_searches': len(df),
        'total_comments': df['Max Comments'].sum(),
        'total_videos': df['Max Videos'].sum(),
        'last_search': df['Timestamp'].iloc[0] if not df.empty else 'Never'
    }
