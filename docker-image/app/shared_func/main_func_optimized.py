from shared_func.youtube_search import search_youtube
import pandas as pd
from shared_func.googleapiclient_func import get_youtube_comments
from shared_func.translate_func import translate_text
from shared_func.text_func import *
from shared_func.nlp_func import *
from shared_func.comprehend_func import sentiment_analysis

def extract_data(search_str, max_videos=1, max_comments=10):
    search_results = search_youtube(search_str, max_results=max_videos)
    
    # Collect all data first
    all_data = []
    
    for result in search_results:
        link = result["link"]
        title = result["title"]
        print(f"Processing: {title}")
        
        comments = get_youtube_comments(link, max_comments)
        if not comments or len(comments) <= 1:
            continue
            
        for person, comment_list in comments.items():
            for comment in comment_list:
                all_data.append({
                    "title": title,
                    "link": link, 
                    "person": person,
                    "comment": comment
                })
    
    if not all_data:
        return pd.DataFrame(columns=["sentiment_score","comment","title","person","link","translated","normalized"])
    
    # Create DataFrame once
    df = pd.DataFrame(all_data)
    
    # Batch translate (if your translate function supports it, otherwise keep individual calls)
    df["translated"] = df["comment"].apply(translate_text)
    df["normalized"] = df["translated"].apply(lambda x: normalize(x) if x is not None else None)
    df['sentiment_score'] = df['normalized'].apply(sentiment_analysis)
    
    # Reorder columns and sort
    df = df[["sentiment_score","comment","title","person","link","translated","normalized"]]
    df = df.sort_values("sentiment_score")
    
    return df
