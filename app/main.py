from shared_func.youtube_search import search_youtube
import os
import pandas as pd
from googleapiclient.discovery import build
from shared_func.googleapiclient_func import *
from collections import Counter
import matplotlib.pyplot as plt
from shared_func.text_func import *
from shared_func.nlp_func import *

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

    return df

def analysing(df):

    df["video_id"] = df["link"].apply(lambda x: x.replace("https://www.youtube.com/watch?v=",""))

    df["normalized"] = df["translated"].apply(lambda x: normalize(x) if x is not None else None)

    groupby_col = 'title'

    df_classes_grouped = df.groupby(groupby_col)['normalized'].sum().reset_index()

    df_classes_grouped['freq_wrds'] = df_classes_grouped["normalized"].apply(Counter)

    df_classes_grouped['most_frequented_wrds'] = df_classes_grouped.apply(lambda row: row['freq_wrds'].most_common(18), axis=1)

    fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(10, 18))

    areas = df_classes_grouped[ groupby_col ].unique()

    for ax, area in zip(axes.flatten(), areas):
      words, frequencies = zip(*df_classes_grouped[df_classes_grouped[ groupby_col ]==area]["most_frequented_wrds"].values[0])
      df2 = pd.DataFrame({'Words': words, 'Frequency': frequencies})
      sns.barplot(y='Words', x='Frequency', data=df2, orient = 'h', ax=ax)
      ax.set_title(area)  # Defina o título de cada subplot

    # Ajuste o layout dos subplots
    plt.tight_layout()
    plt.show()


        
df = extract_data("Raça Rubro-Negra Força Jovem")
