import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.translate_func import translate_text

def test_translate_text():
    """Test AWS Translate functionality"""
    # Test Portuguese to English
    result = translate_text("Olá mundo", "en")
    assert result is not None
    assert isinstance(result, str)
    print(f"Translation result: {result}")

def test_translate_text_same_language():
    """Test translation when source and target are same"""
    result = translate_text("Hello world", "en")
    assert result == "Hello world"

if __name__ == "__main__":
    test_translate_text()
    test_translate_text_same_language()
    print("✅ Translation tests passed")
