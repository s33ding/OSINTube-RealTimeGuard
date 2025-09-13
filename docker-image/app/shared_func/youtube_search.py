from shared_func.googleapiclient_func import connect_to_youtube
import config

def search_youtube(query, max_results=config.search_limit, order_by_date=True):
    """
    Search YouTube for videos using YouTube Data API v3.
    """
    youtube = connect_to_youtube()
    
    order = 'date' if order_by_date else 'relevance'
    
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        order=order,
        maxResults=max_results
    )
    
    response = request.execute()
    
    # Convert to format expected by the app
    results = []
    for item in response['items']:
        result = {
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'link': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'channel': {
                'name': item['snippet']['channelTitle'],
                'id': item['snippet']['channelId']
            },
            'publishedTime': item['snippet']['publishedAt'],
            'thumbnails': item['snippet']['thumbnails']
        }
        results.append(result)
    
    return results

def search_by_channel(channel_url, max_results=config.search_limit, order_by_date=True):
    """
    Search YouTube for videos within a specific channel using YouTube Data API v3.
    """
    youtube = connect_to_youtube()
    
    # Extract channel ID from URL
    channel_id = get_channel_id_from_url(channel_url)
    if not channel_id:
        raise ValueError("Invalid channel URL")
    
    order = 'date' if order_by_date else 'relevance'
    
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order=order,
        maxResults=max_results
    )
    
    response = request.execute()
    
    # Convert to format expected by the app
    results = []
    for item in response['items']:
        result = {
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'link': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'channel': {
                'name': item['snippet']['channelTitle'],
                'id': item['snippet']['channelId']
            },
            'publishedTime': item['snippet']['publishedAt'],
            'thumbnails': item['snippet']['thumbnails']
        }
        results.append(result)
    
    return results

def get_channel_id_from_url(channel_url):
    """Extract channel ID from YouTube channel URL."""
    from urllib.parse import urlparse
    
    parsed_url = urlparse(channel_url)
    if 'youtube.com' in parsed_url.netloc:
        path = parsed_url.path
        if '/channel/' in path:
            return path.split('/channel/')[-1]
        elif '/c/' in path:
            return path.split('/c/')[-1]
        elif '/user/' in path:
            return path.split('/user/')[-1]
        elif '/@' in path:
            return path.split('/@')[-1]
    
    return None
