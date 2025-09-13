import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.dynamodb_func import log_search_to_dynamodb

def test_dynamodb_logging():
    """Test DynamoDB logging functionality"""
    
    # Test data
    video_query = "test search query"
    s3_key = "dataset/test/data.pickle"
    max_comments = 10
    max_videos = 1
    
    try:
        result = log_search_to_dynamodb(video_query, s3_key, max_comments, max_videos)
        assert result == True
        print(f"✅ Successfully logged to DynamoDB")
        print(f"   Query: {video_query}")
        print(f"   S3 Key: {s3_key}")
        print(f"   Max Comments: {max_comments}")
        print(f"   Max Videos: {max_videos}")
        
    except Exception as e:
        print(f"❌ DynamoDB logging failed: {e}")
        raise e

def test_dynamodb_logging_with_special_chars():
    """Test DynamoDB logging with special characters"""
    
    video_query = "test with special chars: áéíóú & symbols!"
    s3_key = "dataset/special-chars/data.pickle"
    max_comments = 50
    max_videos = 3
    
    try:
        result = log_search_to_dynamodb(video_query, s3_key, max_comments, max_videos)
        assert result == True
        print(f"✅ Successfully logged special characters to DynamoDB")
        
    except Exception as e:
        print(f"❌ Special characters logging failed: {e}")
        raise e

if __name__ == "__main__":
    test_dynamodb_logging()
    test_dynamodb_logging_with_special_chars()
    print("✅ DynamoDB tests passed")
