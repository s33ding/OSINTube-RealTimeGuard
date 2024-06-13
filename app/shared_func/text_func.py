import re
from collections import Counter
import nltk
from itertools import islice

def clean_text(text, language="english"):
    txt = re.sub(r"/W"," ",text)
    lst_wrds = [s.lower() for s in txt.split()]
    lst_wrds = rmv_stop_wrds(lst_wrds, language)
    return lst_wrds

def top_20_words(lst_wrds):
    return Counter(lst_wrds).most_common(20)

def rmv_stop_wrds(tokens, language):
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words(language)
    tokens_cleaned=[]
    for item in tokens:
        if (item not in stopwords) and (len(item) > 2):
            tokens_cleaned.append(item)
    return tokens_cleaned

def biagram(tokens):
    # Pair each token with the next one in the list
    paired_tokens = zip(tokens, islice(tokens, 1, None))

    # Join each pair of tokens with a space in between
    biagrams = [' '.join(pair) for pair in paired_tokens]
    freq_words = Counter(biagrams).most_common(20)
    return freq_words 

