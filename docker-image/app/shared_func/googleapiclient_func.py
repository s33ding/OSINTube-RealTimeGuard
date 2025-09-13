import os
import re
import config
from googleapiclient.discovery import build

def connect_to_youtube():
    # Build the YouTube API service using the API key
    youtube = build('youtube', 'v3', developerKey=config.youtube_api_key)
    return youtube

def scrap_youtube_comments(video_url, youtube, max_comments=10):
    # Retrieve comments for a specific video
    video_id = video_url.split("v=")[-1]
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_comments
        ).execute()
        return response
    except:
        return None

def get_youtube_comments(video_url='https://www.youtube.com/watch?v=8OOciVqvalU', max_comments=10):
    youtube = connect_to_youtube()
    result = scrap_youtube_comments(video_url, youtube, max_comments)
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

        # Extract commenter info
        commenter_username = commenter_response['items'][0]['snippet']['title']
        channel_url = f"https://www.youtube.com/channel/{commenter_id}"
        
        # Create separate user info (username only)
        user_info = commenter_username

        if user_info in comments_dict:
            comments_dict[user_info].append({
                'comment': comment,
                'user_channel': channel_url
            })
        else:
            comments_dict[user_info] = [{
                'comment': comment,
                'user_channel': channel_url
            }]

    return comments_dict

def translate_to_english(text):
    """
    Translate text to English using AWS Translate.
    """
    from shared_func.translate_func import translate_text
    return translate_text(text, 'en')


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

