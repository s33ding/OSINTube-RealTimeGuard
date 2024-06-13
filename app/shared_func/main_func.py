from shared_func.youtube_search import search_youtube
import os
import pandas as pd
from googleapiclient.discovery import build
from shared_func.googleapiclient_func import *
from collections import Counter
import matplotlib.pyplot as plt
from shared_func.text_func import *
from shared_func.nlp_func import *
from shared_func.openai_func import *

def extract_data(search_str):
    search_results = search_youtube(search_str)
    links = [result['link'] for result in search_results]

    df = pd.DataFrame()
    dct_comments = {}

    for result in search_results:
        link = result["link"]
        title = result["title"]
        print(f"title: {title}; link:{link}")
        comments = get_youtube_comments(link)

        if comments is None:
            continue
        if len(comments) <= 1:
            continue

        for person in comments.keys():
            for comment in comments.get(person):
                tmp = pd.DataFrame({"title":[title],"link":[link],"person":[person],"comment":[comment],"translated":[translate_to_english(comment)]})
                df = pd.concat([tmp, df])

    df["normalized"] = df["translated"].apply(lambda x: normalize(x) if x is not None else None)
    #df['sentiment_score'] = df['normalized'].apply(analyze_sentiment)
    return df

