import boto3
import json
import config
import re
import hashlib
from datetime import datetime

def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name='us-east-1')

def get_dynamodb_client():
    return boto3.client('dynamodb', region_name='us-east-1')

def get_s3_client():
    return boto3.client('s3', region_name='us-east-1')

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

def threat_analysis(comments_list, dataset_id):
    """
    Analyze comments with sentiment score = 0 for potential threats using LLaMA
    """
    # Check if analysis already exists
    if check_threat_analysis_exists(dataset_id):
        return load_cached_threat_analysis(dataset_id)
    
    # Filter comments with sentiment score = 0
    neutral_comments = [comment for comment in comments_list if comment.get('sentiment_score') == 0.0]
    
    if not neutral_comments:
        return {"status": "no_neutral_comments", "threats": []}
    
    bedrock = get_bedrock_client()
    
    # Combine comments for analysis
    comments_text = "\n".join([f"Comment {i+1}: {comment.get('comment', '')}" 
                              for i, comment in enumerate(neutral_comments)])
    
    prompt = f"""You are a specialized security analyst AI trained to detect potential threats, terrorist activities, and criminal behavior in social media comments. Analyze the following comments with EXTREME PRECISION and NO HALLUCINATION.

CRITICAL INSTRUCTIONS:
- Only flag content that contains EXPLICIT threats, violence, or criminal intent
- Do NOT flag political opinions, criticism, or emotional expressions
- Be conservative in your assessment - false positives are worse than false negatives
- Provide specific evidence for any threat detected

Comments to analyze:
{comments_text}

Respond in JSON format:
{{
  "threat_level": "none|low|medium|high",
  "threats_detected": [
    {{
      "comment_number": 1,
      "threat_type": "violence|terrorism|criminal|harassment",
      "confidence": 0.0-1.0,
      "evidence": "specific text that indicates threat",
      "recommendation": "action to take"
    }}
  ],
  "summary": "brief analysis summary"
}}"""
    
    body = json.dumps({
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "max_gen_len": 1000,
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
        
        # Parse JSON response
        try:
            threat_analysis_result = json.loads(completion)
        except:
            # Fallback if JSON parsing fails
            threat_analysis_result = {
                "threat_level": "none",
                "threats_detected": [],
                "summary": "Analysis completed but response format invalid"
            }
        
        # Cache results in S3 and DynamoDB
        cache_threat_analysis(dataset_id, threat_analysis_result)
        
        return threat_analysis_result
        
    except Exception as e:
        print(f"Threat analysis error: {e}")
        return {"status": "error", "message": str(e)}

def check_threat_analysis_exists(dataset_id):
    """Check if threat analysis already exists for this dataset"""
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.get_item(
            TableName='threat_analysis',
            Key={'dataset_id': {'S': dataset_id}}
        )
        return 'Item' in response
    except:
        return False

def cache_threat_analysis(dataset_id, analysis_result):
    """Cache threat analysis results in S3 and log in DynamoDB"""
    try:
        # Save to S3
        s3 = get_s3_client()
        s3_key = f"threat_analysis/{dataset_id}.json"
        s3.put_object(
            Bucket=config.bucket_name,
            Key=s3_key,
            Body=json.dumps(analysis_result),
            ContentType='application/json'
        )
        
        # Log in DynamoDB
        dynamodb = get_dynamodb_client()
        dynamodb.put_item(
            TableName='threat_analysis',
            Item={
                'dataset_id': {'S': dataset_id},
                'analysis_date': {'S': datetime.now().isoformat()},
                's3_key': {'S': s3_key},
                'threat_level': {'S': analysis_result.get('threat_level', 'none')},
                'threats_count': {'N': str(len(analysis_result.get('threats_detected', [])))}
            }
        )
        
    except Exception as e:
        print(f"Caching error: {e}")

def load_cached_threat_analysis(dataset_id):
    """Load cached threat analysis from S3"""
    try:
        s3 = get_s3_client()
        s3_key = f"threat_analysis/{dataset_id}.json"
        response = s3.get_object(Bucket=config.bucket_name, Key=s3_key)
        return json.loads(response['Body'].read())
    except Exception as e:
        print(f"Cache loading error: {e}")
        return None
