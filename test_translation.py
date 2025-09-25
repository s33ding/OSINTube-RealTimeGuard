#!/usr/bin/env python3
"""
Interactive translation test script for OSINTube-RealTimeGuard
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.shared_func.translate_func import translate_text, detect_language

def test_translation():
    print("🌍 OSINTube Translation Test")
    print("=" * 40)
    
    test_texts = [
        "Hola, ¿cómo estás?",  # Spanish
        "Bonjour, comment allez-vous?",  # French
        "Guten Tag, wie geht es Ihnen?",  # German
        "Ciao, come stai?",  # Italian
        "Olá, como você está?",  # Portuguese
        "こんにちは、元気ですか？",  # Japanese
        "你好，你好吗？",  # Chinese
        "Привет, как дела?",  # Russian
        "Hello, how are you?",  # English
    ]
    
    for text in test_texts:
        detected_lang = detect_language(text)
        translated = translate_text(text, 'en')
        print(f"Original: {text}")
        print(f"Detected: {detected_lang}")
        print(f"English:  {translated}")
        print("-" * 40)

if __name__ == "__main__":
    test_translation()
