import os

comments_maxResult = 25
comments_maxResult = 80
gcp_api_key =  os.environ["GCP_CRED"]
openai_api_key =  os.environ["OPENAI_CRED"]
aws_key =  os.environ["AWS_ACCESS_KEY_ID"]
aws_secret =  os.environ["AWS_SECRET_ACCESS_KEY"]
search_limit = 15
search_limit = 5
bucket_name = "s33ding-osintube"
default_file_name = "data.pickle"
output_path = f"output/{default_file_name}"
delete_file = False
img_path = "media/osintube.webp"

readme = f"""
OSINTube-RealTimeGuard is a real-time threat detection system for YouTube content, ensuring online safety by identifying threats and suspicious activities through continuous monitoring and analysis. It leverages the Google API Client to scrape and translate YouTube comments, YouTubeSearchPython to search for videos, Amazon S3 for data storage, NLP for text tokenization, OpenAI for sentiment analysis, Streamlit for the backend interface, and Docker for easy deployment.
"""

