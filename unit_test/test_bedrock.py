import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.bedrock_func import sentiment_analysis

def test_sentiment_analysis():
    """Test Bedrock sentiment analysis"""
    # Test positive sentiment
    result = sentiment_analysis("I love this video!")
    assert result is not None
    assert isinstance(result, float)
    assert 0 <= result <= 1
    print(f"Positive sentiment: {result}")

def test_sentiment_analysis_negative():
    """Test negative sentiment"""
    result = sentiment_analysis("This is terrible and awful")
    assert result is not None
    assert isinstance(result, float)
    assert 0 <= result <= 1
    print(f"Negative sentiment: {result}")

if __name__ == "__main__":
    test_sentiment_analysis()
    test_sentiment_analysis_negative()
    print("✅ Bedrock tests passed")
