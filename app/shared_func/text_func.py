import re
from collections import Counter
import nltk
from itertools import islice
import unicodedata

def clean_html_tags(text):
    """Remove HTML tags and clean up text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    
    # Remove duplicate hashtags/content
    words = text.split()
    seen = set()
    cleaned_words = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            cleaned_words.append(word)
    
    return ' '.join(cleaned_words)

def normalize_key_name(key_name):
    # Remove accents and special characters
    normalized = unicodedata.normalize('NFD', key_name)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Replace spaces and special characters with underscores
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'[-\s]+', '_', normalized)
    
    return normalized

def normalize(text):
    if not text:
        return ""
    
    # Clean HTML tags first
    text = clean_html_tags(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

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

