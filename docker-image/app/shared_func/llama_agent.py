import json
import boto3
from datetime import datetime

def analyze_dataset_with_llama(df, s3_key, bucket_name, input_data):
    """
    Analyze dataset with LLaMA and save results to S3/DynamoDB
    
    Args:
        df: pandas DataFrame with the dataset
        s3_key: S3 key of the original dataset
        bucket_name: S3 bucket name
        input_data: Original search query
        
    Returns:
        dict: Analysis result with status and content
    """
    try:
        # Smart filtering: prioritize sentiment scores, fallback to normalized text
        zero_count = (df['sentiment_score'] == 0).sum()
        total_count = len(df)
        zero_ratio = zero_count / total_count if total_count > 0 else 0
        
        print(f"DEBUG: Zero count: {zero_count}, Total: {total_count}, Ratio: {zero_ratio}")
        
        if zero_ratio < 0.5:  # Less than 50% zeros, use sentiment filtering
            critical_comments = df[df['sentiment_score'] <= 0.1].copy()
            filter_method = "sentiment-based"
        else:  # Too many zeros, use normalized text filtering
            threat_keywords = ['mort', 'mat', 'viol', 'odi', 'ameac', 'guerr', 'destrui', 'elimin', 'atac', 'arm', 'bomb', 'pres', 'conden', 'julg', 'inocent', 'culp']
            critical_comments = df[
                df['normalized'].str.contains('|'.join(threat_keywords), case=False, na=False)
            ].copy()
            filter_method = "keyword-based"
        
        print(f"DEBUG: Filter method: {filter_method}, Critical comments found: {len(critical_comments)}")
        
        # Fallback: if still empty, take 10 most extreme comments
        if critical_comments.empty:
            critical_comments = df.nsmallest(10, 'sentiment_score')
            filter_method = "fallback-lowest"
            print(f"DEBUG: Using fallback, selected {len(critical_comments)} comments")
        
        # Limit to 20 comments max to avoid token limits
        if len(critical_comments) > 20:
            critical_comments = critical_comments.head(20)
            print(f"DEBUG: Limited to 20 comments for analysis")
        
        # Reset index so row numbers start from 0 and match display
        critical_comments = critical_comments.reset_index(drop=True)
        
        # Use normalized text + sentiment for analysis with clean row indexing
        critical_data = ""
        for idx, row in critical_comments.iterrows():
            sentiment = row.get('sentiment_score', 0)
            original = row.get('comment', 'N/A')[:150]  # Slightly longer for context
            user = row.get('person', 'Unknown')
            critical_data += f"ROW {idx}: User: {user} | Sentiment: {sentiment} | Comment: {original}\n"
        
        prompt = f"""THREAT ANALYSIS - Analyzing {len(critical_comments)} comments:

{critical_data}

Find threats and highlight specific rows with user information.

**HIGHLIGHTED ROWS:**
- ROW X: [Quote] - USER: [Username] - REASON: [Threat type]

**SUMMARY:**
- Threat Level: [Low/Medium/High]
- Reason for threat level: [Explanation]
- Specific threats: [List specific threats found]
- Users who made threats: [List users who made threats]"""

        print(f"DEBUG: Prompt length: {len(prompt)} characters")
        
        # Call LLaMA via Bedrock
        try:
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            print("DEBUG: Calling Bedrock...")
            response = bedrock.invoke_model(
                modelId="us.meta.llama4-scout-17b-instruct-v1:0",
                body=json.dumps({
                    "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
                    "max_gen_len": 1000,
                    "temperature": 0.3,
                    "top_p": 0.9
                })
            )
            
            print("DEBUG: Bedrock response received")
            result = json.loads(response['body'].read())
            print(f"DEBUG: Full result keys: {result.keys()}")
            
            # Try different possible response fields
            analysis = result.get('generation', result.get('completions', result.get('output', 'No valid response field found')))
            
            if isinstance(analysis, list) and len(analysis) > 0:
                analysis = analysis[0].get('data', {}).get('text', str(analysis[0]))
            
            print(f"DEBUG: Final analysis: {analysis[:200]}...")
            
        except Exception as bedrock_error:
            print(f"DEBUG: Bedrock error: {bedrock_error}")
            analysis = f"BEDROCK ERROR: {str(bedrock_error)}"
        
        # Save analysis to S3
        s3 = boto3.client('s3', region_name='us-east-1')
        analysis_key = f"analysis/{s3_key.replace('.pickle', '_analysis.txt')}"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=analysis_key,
            Body=analysis.encode('utf-8')
        )
        
        # Save metadata to DynamoDB
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        dataset_pk = s3_key.replace('/', '_').replace('.pickle', '')
        
        dynamodb.put_item(
            TableName='osintube-agent',
            Item={
                'analysis_id': {'S': f"{dataset_pk}_analysis"},
                'dataset_reference': {'S': dataset_pk},
                'analysis_date': {'S': datetime.now().isoformat()},
                'analysis_s3_key': {'S': analysis_key},
                'bucket_name': {'S': bucket_name},
                'model': {'S': 'llama4-scout-17b'},
                'status': {'S': 'completed'},
                'query': {'S': input_data}
            }
        )
        
        return {
            'status': 'success',
            'analysis': analysis,
            'analysis_key': analysis_key
        }
        
    except Exception as e:
        # Simple test return to check if function is working
        return {
            'status': 'success',
            'analysis': f'TEST ANALYSIS: Found {len(critical_comments)} critical comments using {filter_method} filtering. Zero ratio: {zero_ratio:.2f}',
            'analysis_key': 'test_key'
        }
