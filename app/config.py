import os

comments_maxResult = 80
comments_maxResult = 20
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

readme = f"""OSINTube-RealTimeGuard is a real-time threat detection system for YouTube content. It leverages AWS YouTube Search and PyTube for efficient video retrieval and transcription. With continuous monitoring and analysis, this system ensures online safety by identifying potential threats and suspicious activities in YouTube videos."""

