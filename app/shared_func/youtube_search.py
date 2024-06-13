from youtubesearchpython import VideosSearch
from youtubesearchpython import VideoSortOrder
from youtubesearchpython import CustomSearch
from urllib.parse import urlparse, parse_qs
import config

def search_youtube(query, max_results=config.search_limit, order_by_date=True):
    """
    Search YouTube for videos based on the given query and optional filters.

    Args:
        query (str): The search query.
        max_results (int): Maximum number of search results to return. Default is 10.

    Returns:
        list: A list of dictionaries containing information about the search results.
    """

    if order_by_date:
        if max_results is None:
            videos_search = VideosSearch(query, limit=max_results) 
        else:
            videos_search = CustomSearch(query, VideoSortOrder.uploadDate, limit=max_results) 
    else:
        if max_results is None:
            videos_search = CustomSearch(query, VideoSortOrder.uploadDate) 
        else:
            videos_search = VideosSearch(query, limit=max_results) 

    results = videos_search.result()['result']
    return results


def get_channel_id_from_url(channel_url):
    """
    Extracts the channel ID from a YouTube channel URL.

    Args:
        channel_url (str): The URL of the YouTube channel.

    Returns:
        str: The channel ID extracted from the URL.
    """
    parsed_url = urlparse(channel_url)
    if parsed_url.netloc == 'www.youtube.com':
        if parsed_url.path == '/channel':
            query_params = parse_qs(parsed_url.query)
            channel_id = query_params.get('channel_id', [''])[0]
            return channel_id
        elif parsed_url.path.startswith('/user/'):
            return parsed_url.path.split('/')[-1]
        elif parsed_url.path.startswith('/c/'):
            return parsed_url.path.split('/')[-1]
        else:
            # Extract channel ID from URL in the format '/@username'
            return parsed_url.path.split('/')[-1].replace('@', '')
    return None


def search_by_channel(channel_url, max_results=config.search_limit, order_by_date=True):
    """
    Search YouTube for videos within a specific channel.

    Args:
        channel_url (str): The URL of the YouTube channel to search within.
        max_results (int): Maximum number of search results to return. Default is 10.
        order_by_date (bool): Whether to order search results by date. Default is True.

    Returns:
        list: A list of dictionaries containing information about the search results.
    """

    channel_id = get_channel_id_from_url(channel_url)

    if not channel_id:
        raise ValueError("Invalid channel URL. Please provide a valid YouTube channel URL.")

    if order_by_date:
        if max_results is None:
            videos_search = CustomSearch('', limit=max_results, channel=channel_id)
        else:
            videos_search = CustomSearch('', VideoSortOrder.uploadDate, limit=max_results, channel=channel_id)
    else:
        if max_results is None:
            videos_search = CustomSearch('', VideoSortOrder.uploadDate, channel=channel_id)
        else:
            videos_search = CustomSearch('', limit=max_results, channel=channel_id)

    results = videos_search.result()['result']
    return results
