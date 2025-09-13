import boto3
import json
import config
import re

def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name='us-east-1')

def sentiment_analysis(transcription):
    """
    Analyze sentiment using Amazon Bedrock Llama model
    """
    if isinstance(transcription, list):
        transcription = ", ".join(transcription)
    
    bedrock = get_bedrock_client()
    
    prompt = f"""Analyze the sentiment of this text and provide a numerical score between 0 and 1, where 0 is very negative and 1 is very positive.

Text: {transcription}

Respond with only the numerical score (e.g., 0.7):"""
    
    body = json.dumps({
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "max_gen_len": 50,
        "temperature": 0.1,
        "top_p": 0.9
    })
    
    try:
        response = bedrock.invoke_model(
            modelId=config.bedrock_model_id,
            body=body
        )
        
        result = json.loads(response['body'].read())
        completion = result['generation'].strip()
        
        # Extract numeric score using regex
        match = re.search(r"[-+]?\d*\.\d+|\d+", completion)
        if match:
            sentiment_score = float(match.group())
            # Ensure score is between 0 and 1
            return max(0, min(1, sentiment_score))
        else:
            return 0.5  # Default neutral score
            
    except Exception as e:
        print(f"Bedrock error: {e}")
        return 0.5  # Default neutral score
