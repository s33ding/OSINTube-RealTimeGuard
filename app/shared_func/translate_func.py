import boto3
import logging

logger = logging.getLogger(__name__)

def get_translate_client():
    return boto3.client('translate', region_name='us-east-1')

def get_comprehend_client():
    return boto3.client('comprehend', region_name='us-east-1')

def detect_language(text):
    """Detect the language of the input text using AWS Comprehend"""
    if not text or len(text.strip()) < 3:
        return 'auto'
    
    comprehend = get_comprehend_client()
    try:
        response = comprehend.detect_dominant_language(Text=text)
        languages = response.get('Languages', [])
        if languages and languages[0]['Score'] > 0.5:
            return languages[0]['LanguageCode']
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
    return 'auto'

def translate_text(text, target_language='en', source_language=None):
    """
    Translate text using AWS Translate with automatic language detection
    """
    if not text or not text.strip():
        return text
    
    translate = get_translate_client()
    
    # If no source language specified, detect it
    if source_language is None:
        source_language = detect_language(text)
    
    # If detected language is same as target, return original
    if source_language == target_language:
        return text
    
    try:
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        return response['TranslatedText']
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        # Fallback to auto-detection
        try:
            response = translate.translate_text(
                Text=text,
                SourceLanguageCode='auto',
                TargetLanguageCode=target_language
            )
            return response['TranslatedText']
        except Exception as e2:
            logger.error(f"Auto-translation also failed: {e2}")
            return text
