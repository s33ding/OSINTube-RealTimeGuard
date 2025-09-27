import boto3
import json
import config
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name='us-east-1')

from shared_func.boto3_session import create_boto3_session

def get_dynamodb_client():
    session = create_boto3_session()
    return session.client('dynamodb', region_name='us-east-1')

def get_s3_client():
    return boto3.client('s3', region_name='us-east-1')

def sentiment_analysis(transcription):
    """
    Enhanced sentiment analysis using Amazon Bedrock Llama model
    """
    if isinstance(transcription, list):
        transcription = ", ".join(transcription)
    
    # Clean and validate input
    if not transcription or len(transcription.strip()) == 0:
        return 0.5
    
    bedrock = get_bedrock_client()
    
    prompt = f"""Analyze the sentiment of this text and provide a numerical score between 0 and 1, where:
- 0.0-0.2: Very negative (threats, hate, extreme anger)
- 0.2-0.4: Negative (criticism, disappointment, mild anger)
- 0.4-0.6: Neutral (factual, balanced)
- 0.6-0.8: Positive (supportive, happy)
- 0.8-1.0: Very positive (enthusiastic, loving)

Text: {transcription[:500]}

Respond with only the numerical score (e.g., 0.3):"""
    
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
        print(f"Bedrock sentiment analysis error: {e}")
        return 0.5  # Default neutral score

def enhanced_threat_analysis(comments_list: List[Dict], dataset_id: str, query_context: str = "") -> Dict:
    """
    Enhanced threat analysis with multi-layered detection and scoring
    """
    # Check if analysis already exists
    if check_threat_analysis_exists(dataset_id):
        cached_result = load_cached_threat_analysis(dataset_id)
        if cached_result:
            return cached_result
    
    # Enhanced filtering: multiple criteria
    high_risk_comments = []
    
    for comment in comments_list:
        sentiment = comment.get('sentiment_score', 0.5)
        text = comment.get('comment', '')
        
        # Multi-criteria risk assessment
        risk_score = calculate_risk_score(text, sentiment)
        
        if risk_score > 0.6:  # High risk threshold
            comment['risk_score'] = risk_score
            high_risk_comments.append(comment)
    
    # Sort by risk score
    high_risk_comments.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
    
    if not high_risk_comments:
        return {"status": "no_high_risk_comments", "threats": [], "risk_level": "low"}
    
    # Limit to top 15 for analysis
    analysis_comments = high_risk_comments[:15]
    
    bedrock = get_bedrock_client()
    
    # Build enhanced analysis prompt
    comments_data = []
    for i, comment in enumerate(analysis_comments):
        risk_score = comment.get('risk_score', 0)
        sentiment = comment.get('sentiment_score', 0)
        text = comment.get('comment', '')[:200]
        user = comment.get('person', 'Unknown')
        
        comments_data.append(f"Comment {i+1}: [Risk: {risk_score:.2f}] [Sentiment: {sentiment:.2f}] User: {user} | Text: {text}")
    
    comments_text = "\n".join(comments_data)
    
    prompt = f"""🤖 ADVANCED THREAT DETECTION SYSTEM

CONTEXT: Analyzing comments related to "{query_context}"

HIGH-RISK COMMENTS (Pre-filtered by AI scoring):
{comments_text}

ANALYSIS MISSION:
You are an elite security analyst AI. Analyze these pre-filtered high-risk comments with SURGICAL PRECISION.

DETECTION PRIORITIES:
1. EXPLICIT THREATS: Direct threats of violence, harm, or illegal action
2. INCITEMENT: Calls for violence, riots, or illegal activities  
3. HATE SPEECH: Targeted harassment based on identity/beliefs
4. EXTREMIST CONTENT: Radical ideologies promoting violence
5. COORDINATED ATTACKS: Evidence of organized harmful activities

CRITICAL INSTRUCTIONS:
- Only flag content with CLEAR, UNAMBIGUOUS threats or hate
- Consider context of query: "{query_context}"
- Distinguish between criticism/anger vs actual threats
- Provide specific evidence for each threat identified
- Rate confidence level (0.0-1.0) for each assessment

OUTPUT FORMAT (JSON only):
{{
  "overall_threat_level": "none|low|medium|high|critical",
  "total_threats_found": 0,
  "threats_detected": [
    {{
      "comment_id": 1,
      "threat_type": "violence|incitement|hate_speech|extremism|harassment",
      "severity": "low|medium|high|critical",
      "confidence": 0.0-1.0,
      "evidence": "specific threatening language found",
      "target": "who/what is being threatened",
      "recommendation": "immediate_action|monitor|investigate|report_authorities",
      "user": "username",
      "risk_indicators": ["caps", "profanity", "direct_threat", "etc"]
    }}
  ],
  "risk_assessment": {{
    "immediate_danger": true/false,
    "coordinated_activity": true/false,
    "escalation_potential": "low|medium|high",
    "primary_concerns": ["list", "of", "main", "issues"]
  }},
  "summary": "Brief executive summary of findings",
  "recommendations": [
    "Specific action items based on threat level"
  ]
}}"""
    
    body = json.dumps({
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "max_gen_len": 1500,
        "temperature": 0.1,
        "top_p": 0.85
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
            
            # Add metadata
            threat_analysis_result['analysis_metadata'] = {
                'comments_analyzed': len(analysis_comments),
                'total_comments': len(comments_list),
                'analysis_date': datetime.now().isoformat(),
                'model': config.bedrock_model_id,
                'query_context': query_context
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            threat_analysis_result = {
                "overall_threat_level": "medium",
                "total_threats_found": len([c for c in analysis_comments if c.get('risk_score', 0) > 0.8]),
                "threats_detected": [],
                "summary": f"Analysis completed but response format invalid. Found {len(analysis_comments)} high-risk comments.",
                "status": "parsing_error",
                "raw_response": completion[:500]
            }
        
        # Cache results
        cache_threat_analysis(dataset_id, threat_analysis_result)
        
        return threat_analysis_result
        
    except Exception as e:
        print(f"Enhanced threat analysis error: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "overall_threat_level": "unknown",
            "total_threats_found": 0
        }

def calculate_risk_score(text: str, sentiment: float) -> float:
    """
    Calculate comprehensive risk score for a comment
    """
    if not text:
        return 0.0
    
    text_lower = text.lower()
    risk_score = 0.0
    
    # Base score from sentiment (inverted - lower sentiment = higher risk)
    risk_score += (1 - sentiment) * 0.4
    
    # Threat keywords (weighted by severity)
    high_threat_keywords = ['kill', 'murder', 'death', 'bomb', 'shoot', 'attack', 'destroy', 'eliminate']
    medium_threat_keywords = ['hate', 'revenge', 'payback', 'consequences', 'warning', 'threat']
    
    for keyword in high_threat_keywords:
        if keyword in text_lower:
            risk_score += 0.3
    
    for keyword in medium_threat_keywords:
        if keyword in text_lower:
            risk_score += 0.15
    
    # Behavioral indicators
    caps_ratio = len(re.findall(r'[A-Z]', text)) / max(len(text), 1)
    if caps_ratio > 0.3:  # More than 30% caps
        risk_score += 0.1
    
    exclamation_count = text.count('!')
    if exclamation_count > 2:
        risk_score += 0.1
    
    # Personal pronouns indicating direct targeting
    if re.search(r'\byou\b|\byour\b', text_lower):
        risk_score += 0.1
    
    # Urgency indicators
    urgency_words = ['now', 'today', 'immediate', 'urgent', 'asap']
    for word in urgency_words:
        if word in text_lower:
            risk_score += 0.05
    
    return min(risk_score, 1.0)  # Cap at 1.0

def threat_analysis(comments_list, dataset_id):
    """
    Legacy function - redirects to enhanced version
    """
    return enhanced_threat_analysis(comments_list, dataset_id)

def check_threat_analysis_exists(dataset_id):
    """Check if threat analysis already exists for this dataset"""
    try:
        dynamodb = get_dynamodb_client()
        response = dynamodb.get_item(
            TableName='threat_analysis',
            Key={'dataset_id': {'S': dataset_id}}
        )
        return 'Item' in response
    except Exception as e:
        print(f"Error checking threat analysis existence: {e}")
        return False

def cache_threat_analysis(dataset_id, analysis_result):
    """Cache threat analysis results in S3 and log in DynamoDB"""
    try:
        # Save to S3
        s3 = get_s3_client()
        s3_key = f"threat_analysis/{dataset_id}_enhanced.json"
        s3.put_object(
            Bucket=config.bucket_name,
            Key=s3_key,
            Body=json.dumps(analysis_result, indent=2),
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
                'threat_level': {'S': analysis_result.get('overall_threat_level', 'unknown')},
                'threats_count': {'N': str(analysis_result.get('total_threats_found', 0))},
                'model_version': {'S': 'enhanced_v2'},
                'status': {'S': 'completed'}
            }
        )
        
    except Exception as e:
        print(f"Caching error: {e}")

def load_cached_threat_analysis(dataset_id):
    """Load cached threat analysis from S3"""
    try:
        s3 = get_s3_client()
        s3_key = f"threat_analysis/{dataset_id}_enhanced.json"
        response = s3.get_object(Bucket=config.bucket_name, Key=s3_key)
        return json.loads(response['Body'].read())
    except Exception as e:
        print(f"Cache loading error: {e}")
        return None

def batch_sentiment_analysis(texts: List[str]) -> List[float]:
    """
    Analyze sentiment for multiple texts efficiently
    """
    results = []
    for text in texts:
        score = sentiment_analysis(text)
        results.append(score)
    return results
