import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import pandas as pd
from shared_func.main_func import extract_data
from shared_func.comprehend_func import sentiment_analysis

def test_sentiment_analysis_with_list():
    """Test sentiment analysis with different data types"""
    
    # Test with string (should work)
    result = sentiment_analysis("This is a test comment")
    print(f"String input result: {result}")
    
    # Test with list (should fail - this is likely the issue)
    try:
        result = sentiment_analysis(["This", "is", "a", "list"])
        print(f"List input result: {result}")
    except Exception as e:
        print(f"❌ Error with list input: {e}")
    
    # Test with None
    result = sentiment_analysis(None)
    print(f"None input result: {result}")
    
    # Test with empty string
    result = sentiment_analysis("")
    print(f"Empty string result: {result}")

def test_extract_data_with_real_search():
    """Test extract_data with a search that might return comments"""
    try:
        # Use a popular search term that should have comments
        df = extract_data("python tutorial", max_videos=1, max_comments=3)
        
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        if not df.empty:
            print("Sample data:")
            print(df.head())
            
            # Check data types
            for col in df.columns:
                print(f"{col}: {df[col].dtype}")
                if col == 'comment':
                    print(f"Sample comments: {df[col].head().tolist()}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error in extract_data: {e}")
        import traceback
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    print("Testing sentiment analysis with different inputs...")
    test_sentiment_analysis_with_list()
    
    print("\nTesting extract_data with real search...")
    test_extract_data_with_real_search()
    
    print("✅ Detailed tests completed")
