import boto3
from botocore.exceptions import ClientError

# Function to retrieve table schema information from an AWS Glue catalog
def glue_retrieves_table_details(session, database_name, table_name):
    try:
        glue_client = session.client('glue')
        response = client.get_table(DatabaseName=database_name, Name=table_name)
        response = response["Table"]["StorageDescriptor"]["Columns"]
        return response
    except ClientError as e:
        raise Exception("boto3 client error in retrieves_table_details: " + e.__str__())
    except Exception as e:
        raise Exception("Unexpected error in retrieves_table_details: " + e.__str__())

def start_crawler(session, crawler_name):
    # Create an AWS Glue client
    client = session.client('glue')
    # Start the crawler
    try:
        response = client.start_crawler(Name=crawler_name)
        print(f"Crawler '{crawler_name}' started successfully.")
        return response
    except Exception as e:
        print(f"Failed to start crawler: {e}")

