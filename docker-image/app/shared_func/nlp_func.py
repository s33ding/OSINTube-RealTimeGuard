#normalização
import re
import nltk
nltk.download('stopwords')

stopwords = nltk.corpus.stopwords.words('english')

def tokenizer_rmv_nmb(texto):
  return re.findall(r'[a-zá-ú]+',texto)

def rmv_stopwords(palavras, stopwords=stopwords):
    return [palavra for palavra in palavras if (palavra not in stopwords) and (len(palavra)>1) ]

def rmv_nmb_and_special_chars(txt):
    return re.sub(r'[\dº&$:#]+', '', txt)


def normalize(txt):
    txt = rmv_nmb_and_special_chars(txt)
    txt = rmv_emoticons(txt)
    txt = rmv_stopwords(tokenizer_rmv_nmb(txt.lower()))
    return txt

def rmv_emoticons(text):
    # Define a regular expression pattern to match emoticons
    emoticon_pattern = r'[:;=8][\'\-]?[)D(\[pP/\\@|3]|<3|:\*|;-?\)|:\'\(|:-o|:-?S|8-?[)D]|:-?c|:-?\/|:-?\\|\^_?\^|\(-?_?\)|:O|=O|:-?0|:-?\||:-?x|:-?v|:-[|\\]|:-?\<|:-?3|:\-$|;-?\]|:-?\(|:-?\||:-?\\|:-?\*|:-\!|\(-?\:|:-?Q|:-?L|X-?D|O\_o|:-?B|:-?&|:-?\$|:-?@|:-?'
    # Remove emoticons from the text using the regular expression pattern
    cleaned_text = re.sub(emoticon_pattern, '', text)
    return cleaned_text
