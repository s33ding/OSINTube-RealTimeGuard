import boto3
import json

def get_comprehend_client():
    return boto3.client('comprehend', region_name='us-east-1')

def sentiment_analysis(text):
    """
    Analyze sentiment using Amazon Comprehend
    Returns a score between 0 and 1 (0=negative, 1=positive)
    """
    # Handle different input types
    if text is None:
        return 0.5
    
    # Convert list to string if needed
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    
    # Convert to string and check if empty
    text_str = str(text).strip()
    if not text_str:
        return 0.5  # Neutral for empty text
    
    comprehend = get_comprehend_client()
    
    try:
        response = comprehend.detect_sentiment(
            Text=text_str[:5000],  # Comprehend has 5000 char limit
            LanguageCode='en'
        )
        
        # Get sentiment scores
        sentiment = response['Sentiment']
        scores = response['SentimentScore']
        
        # Convert to 0-1 scale
        if sentiment == 'POSITIVE':
            return scores['Positive']
        elif sentiment == 'NEGATIVE':
            return scores['Negative'] * 0  # Convert negative to low score
        elif sentiment == 'NEUTRAL':
            return 0.5
        else:  # MIXED
            return scores['Positive'] * 0.7  # Slightly positive for mixed
            
    except Exception as e:
        print(f"Comprehend error: {e}")
        return 0.5  # Default neutral score
