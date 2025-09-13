import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import pandas as pd
from shared_func.main_func import extract_data

def test_extract_data_structure():
    """Test extract_data returns proper DataFrame structure"""
    try:
        df = extract_data("test", max_videos=1, max_comments=5)
        
        # Check if DataFrame is returned
        assert isinstance(df, pd.DataFrame)
        
        # Check required columns exist
        expected_columns = ["sentiment_score", "comment", "title", "person", "link", "translated", "normalized"]
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"
        
        print(f"✅ DataFrame structure correct: {df.columns.tolist()}")
        print(f"✅ DataFrame shape: {df.shape}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error in extract_data: {e}")
        raise e

if __name__ == "__main__":
    df = test_extract_data_structure()
    print("✅ Main function tests passed")
