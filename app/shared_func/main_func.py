from shared_func.youtube_search import search_youtube
import os
import pandas as pd
from googleapiclient.discovery import build
from shared_func.googleapiclient_func import get_youtube_comments
from shared_func.translate_func import translate_text
from collections import Counter
import matplotlib.pyplot as plt
from shared_func.text_func import *
from shared_func.nlp_func import *
from shared_func.comprehend_func import sentiment_analysis

def extract_data(search_str, max_videos=1, max_comments=10):
    search_results = search_youtube(search_str, max_results=max_videos)
    links = [result['link'] for result in search_results]

    # Initialize empty DataFrame with required columns
    df = pd.DataFrame(columns=["title", "link", "person", "user_channel", "comment", "translated"])
    
    for result in search_results:
        link = result["link"]
        title = result["title"]
        print(f"title: {title}; link:{link}")
        comments = get_youtube_comments(link, max_comments)

        if comments is None:
            continue
        if len(comments) <= 1:
            continue

        for person in comments.keys():
            for comment_data in comments.get(person):
                # Handle new structure with separate comment and channel info
                if isinstance(comment_data, dict):
                    comment = comment_data['comment']
                    user_channel = comment_data['user_channel']
                else:
                    # Fallback for old structure
                    comment = comment_data
                    user_channel = ""
                
                # Clean HTML tags from comment
                cleaned_comment = clean_html_tags(comment) if comment else comment
                tmp = pd.DataFrame({
                    "title": [title],
                    "link": [link],
                    "person": [person],
                    "user_channel": [user_channel],
                    "comment": [cleaned_comment],
                    "translated": [translate_text(cleaned_comment)]
                })
                df = pd.concat([tmp, df])

    # Only process if we have data
    if not df.empty:
        df["normalized"] = df["translated"].apply(lambda x: normalize(x) if x is not None else None)
        df['sentiment_score'] = df['normalized'].apply(sentiment_analysis)
        df = df[["sentiment_score","comment","title","person","user_channel","link","translated","normalized"]]
        df = df.sort_values("sentiment_score")
    else:
        # Return empty DataFrame with all required columns
        df = pd.DataFrame(columns=["sentiment_score","comment","title","person","user_channel","link","translated","normalized"])
    
    return df

