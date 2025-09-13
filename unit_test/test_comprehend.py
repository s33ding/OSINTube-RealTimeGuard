import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.comprehend_func import sentiment_analysis

def test_comprehend_positive():
    """Test positive sentiment with Comprehend"""
    result = sentiment_analysis("I love this video! It's amazing and wonderful!")
    assert result is not None
    assert isinstance(result, float)
    assert 0 <= result <= 1
    print(f"Positive sentiment: {result}")

def test_comprehend_negative():
    """Test negative sentiment with Comprehend"""
    result = sentiment_analysis("This is terrible and awful. I hate it!")
    assert result is not None
    assert isinstance(result, float)
    assert 0 <= result <= 1
    print(f"Negative sentiment: {result}")

def test_comprehend_neutral():
    """Test neutral sentiment with Comprehend"""
    result = sentiment_analysis("This is a video about something.")
    assert result is not None
    assert isinstance(result, float)
    assert 0 <= result <= 1
    print(f"Neutral sentiment: {result}")

if __name__ == "__main__":
    test_comprehend_positive()
    test_comprehend_negative()
    test_comprehend_neutral()
    print("✅ Comprehend tests passed")
