import boto3

def get_translate_client():
    return boto3.client('translate', region_name='us-east-1')

def translate_text(text, target_language='en'):
    """
    Translate text using AWS Translate
    """
    translate = get_translate_client()
    
    try:
        # Try to translate from auto-detected language
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode=target_language
        )
        return response['TranslatedText']
    except:
        # If auto-detection fails, assume Portuguese and translate
        try:
            response = translate.translate_text(
                Text=text,
                SourceLanguageCode='pt',
                TargetLanguageCode=target_language
            )
            return response['TranslatedText']
        except:
            # If translation fails, return original text
            return text
