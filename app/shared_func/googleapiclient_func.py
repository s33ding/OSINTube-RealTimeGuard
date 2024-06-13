import os
import re
import config
from googleapiclient.discovery import build
from google.oauth2 import service_account

def connect_to_youtube():
    # Build the YouTube API service using the credentials
    youtube = build('youtube', 'v3', developerKey=config.gcp_api_key)
    return youtube

def scrap_youtube_comments(video_url, youtube):
    # Retrieve comments for a specific video
    video_id = video_url.split("v=")[-1]
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=config.comments_maxResult  # Adjust as needed
        ).execute()
        return response
    except:
        return None

def get_youtube_comments(video_url='https://www.youtube.com/watch?v=8OOciVqvalU'):
    youtube = connect_to_youtube()
    result = scrap_youtube_comments(video_url, youtube)
    if result is None:
        return None
    else:
        return analyse(result , youtube)

def analyse(response, youtube):
    comments_dict = {}
    for item in response['items']:
        commenter_id = item['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']

        # Retrieve commenter details
        commenter_response = youtube.channels().list(
            part='snippet',
            id=commenter_id
        ).execute()

        # Extract commenter username
        commenter_username = commenter_response['items'][0]['snippet']['title']

        if commenter_username in comments_dict:
            comments_dict[commenter_username].append(comment)
        else:
            comments_dict[commenter_username] = [comment]

    return comments_dict

def translate_to_english(text):
    """
    Translate text from Portuguese to English using Google Translate API.

    Args:
    - text (str): The text to be translated from Portuguese to English.

    Returns:
    - translated_text (str): The translated text in English.
    """
    # Initialize the Translate API client
    service = build('translate', 'v2', developerKey=config.gcp_api_key)

    # Perform translation
    translation = service.translations().list(
        source='pt',
        target='en',
        q=[text]
    ).execute()

    translated_text = translation['translations'][0]['translatedText']
    return translated_text


def extract_video_id(youtube_url):
    # Regular expression pattern to match YouTube video IDs
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com(?:/[^/]+/.+/.+|/[^/]+/.+|/[^/]+/[^/?]+(?:\?[^/]+=[^/]+(?:&[^/]+=[^/]+)*)?)|youtu\.be/)([a-zA-Z0-9_-]{11})'

    # Search for the video ID in the URL using the pattern
    match = re.search(pattern, youtube_url)

    if match:
        # Extract the video ID from the matched group
        video_id = match.group(1)
        return video_id
    else:
        return None

