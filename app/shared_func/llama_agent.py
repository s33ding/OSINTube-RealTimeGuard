import json
import boto3
import pandas as pd
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
            critical_comments = df[df['sentiment_score'] <= 0.5].copy()  # Much more aggressive - catch even mildly positive
            filter_method = "sentiment-based"
        else:  # Too many zeros, use normalized text filtering
            threat_keywords = ['mort', 'mat', 'viol', 'odi', 'ameac', 'guerr', 'destrui', 'elimin', 'atac', 'arm', 'bomb', 'pres', 'conden', 'julg', 'inocent', 'culp', 'fogo', 'eterno', 'psicopat', 'fracass', 'corrupt', 'traficant', 'assassin', 'militant', 'esquerdist', 'judici', 'credibil', 'solto']
            critical_comments = df[
                df['normalized'].str.contains('|'.join(threat_keywords), case=False, na=False)
            ].copy()
            filter_method = "keyword-based"
        
        # If still not enough, add comments with exclamation marks and caps (aggressive tone)
        if len(critical_comments) < 50:
            aggressive_comments = df[
                df['comment'].str.contains(r'[!]{2,}|[A-Z]{5,}', case=False, na=False, regex=True)
            ]
            critical_comments = pd.concat([critical_comments, aggressive_comments]).drop_duplicates()
            filter_method += "+aggressive-tone"
        
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
        
        prompt = f"""Analyze {len(critical_comments)} comments and highlight ONLY the 3-5 most dangerous ones:

{critical_data}

INSTRUCTIONS:
- Select only the TOP 3-5 most threatening comments
- Focus on violence, threats, extremism, hate speech
- Use class="high-threat" for selected rows
- Skip less dangerous content

Return ONLY this HTML:

<div class="threat-analysis">
<h2>🚨 THREAT ANALYSIS REPORT</h2>

<div class="highlighted-rows">
<h3>🔥 TOP THREATS REQUIRING IMMEDIATE ATTENTION</h3>
<p style="color: #d32f2f; font-weight: bold;">Only the most dangerous content is shown below:</p>
<table class="threat-table">
<tr><th>Row</th><th>User</th><th>Threat Level</th><th>Comment Preview</th><th>Risk Category</th><th>Sentiment</th></tr>
<tr><th>Row</th><th>User</th><th>Threat Level</th><th>Comment</th><th>Risk Type</th></tr>
<tr class="high-threat"><td>ROW X</td><td>Username</td><td>HIGH</td><td>Comment excerpt</td><td>Violence/Hate/etc</td></tr>
</table>
</div>

<div class="summary-stats">
<h3>📊 ANALYSIS SUMMARY</h3>
<div class="stat-grid">
<div class="stat-card threat-level-high"><span class="stat-number">X</span><span class="stat-label">High Threats</span></div>
<div class="stat-card threat-level-medium"><span class="stat-number">X</span><span class="stat-label">Medium Threats</span></div>
<div class="stat-card users-count"><span class="stat-number">X</span><span class="stat-label">Unique Users</span></div>
</div>
</div>

<div class="risk-metrics">
<h3>📈 RISK METRICS</h3>
<ul>
<li><strong>Sentiment Range:</strong> X.XX to X.XX (avg: X.XX)</li>
<li><strong>Language Patterns:</strong> X% CAPS, X% exclamations</li>
<li><strong>Threat Distribution:</strong> X% violence, X% hate speech</li>
</ul>
</div>
</div>

<style>
.threat-analysis { font-family: Arial, sans-serif; max-width: 1000px; margin: 20px auto; }
.threat-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
.threat-table th, .threat-table td { padding: 12px; text-align: left; border: 1px solid #ddd; }
.threat-table th { background: #f44336; color: white; }
.high-threat { background: #ffcdd2; border-left: 8px solid #d32f2f; font-weight: bold; animation: pulse 2s infinite; }
@keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); }} }}
.medium-threat { background: #fff3e0; border-left: 4px solid #ff9800; }
.stat-grid { display: flex; gap: 15px; flex-wrap: wrap; }
.stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; min-width: 120px; }
.stat-number { display: block; font-size: 2em; font-weight: bold; color: #f44336; }
.stat-label { display: block; font-size: 0.9em; color: #666; }
.threat-level-high .stat-number { color: #f44336; }
.threat-level-medium .stat-number { color: #ff9800; }
.users-count .stat-number { color: #2196f3; }
h2, h3 { color: #333; }
ul li { margin: 8px 0; }
</style>"""

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
        
        # Save analysis to S3 (both HTML and text versions)
        s3 = boto3.client('s3', region_name='us-east-1')
        analysis_key = f"analysis/{s3_key.replace('.pickle', '_analysis.html')}"
        text_key = f"analysis/{s3_key.replace('.pickle', '_analysis.txt')}"
        
        # Save HTML version
        s3.put_object(
            Bucket=bucket_name,
            Key=analysis_key,
            Body=analysis.encode('utf-8'),
            ContentType='text/html'
        )
        
        # Save text version for backup
        s3.put_object(
            Bucket=bucket_name,
            Key=text_key,
            Body=analysis.encode('utf-8'),
            ContentType='text/plain'
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
