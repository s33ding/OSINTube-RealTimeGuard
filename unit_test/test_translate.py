import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.translate_func import translate_text, detect_language

def test_detect_language():
    """Test language detection"""
    # Test Portuguese
    lang = detect_language("Olá mundo")
    print(f"Detected language for 'Olá mundo': {lang}")
    
    # Test English
    lang = detect_language("Hello world")
    print(f"Detected language for 'Hello world': {lang}")

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

def test_translate_empty_text():
    """Test translation with empty text"""
    result = translate_text("", "en")
    assert result == ""
    
    result = translate_text(None, "en")
    assert result is None

def test_translate_multiple_languages():
    """Test translation from various languages"""
    test_cases = [
        ("Hola mundo", "es", "en"),  # Spanish to English
        ("Bonjour le monde", "fr", "en"),  # French to English
        ("Ciao mondo", "it", "en"),  # Italian to English
    ]
    
    for text, source, target in test_cases:
        result = translate_text(text, target, source)
        print(f"'{text}' ({source}) -> '{result}' ({target})")
        assert result is not None

if __name__ == "__main__":
    test_detect_language()
    test_translate_text()
    test_translate_text_same_language()
    test_translate_empty_text()
    test_translate_multiple_languages()
    print("✅ All translation tests passed")
