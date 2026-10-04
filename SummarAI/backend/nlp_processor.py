"""Preprocessing: cleaning, tokenization, stop-words, frequency analysis."""
import re
from collections import Counter
import nltk
from nltk.stem import PorterStemmer

def _ensure(res, path):
    try: nltk.data.find(path)
    except LookupError:
        try: nltk.download(res, quiet=True)
        except Exception: pass

for r, p in [("punkt", "tokenizers/punkt"), ("punkt_tab", "tokenizers/punkt_tab"), ("stopwords", "corpora/stopwords")]:
    _ensure(r, p)

try:
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))
except Exception:  # offline fallback list
    STOP = set("a an the and or but if of to in on at by for with from as is are was were be been it its this that these those he she they we you i not no so than then there their his her our your will would can could should may might do does did have has had".split())

stemmer = PorterStemmer()

def clean_text(t):
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    return re.sub(r"\n{2,}", "\n", t).strip()

def sentences(t):
    try: s = nltk.sent_tokenize(t)
    except Exception: s = re.split(r"(?<=[.!?])\s+", t)
    return [x.strip() for x in s if x.strip()]

def words(t):
    try: return nltk.word_tokenize(t)
    except Exception: return re.findall(r"\w+|[^\w\s]", t)

def content_tokens(sentence):
    """Lower-cased alphabetic words, stop-words removed, stemmed."""
    return [stemmer.stem(w.lower()) for w in words(sentence)
            if w.isalpha() and len(w) > 2 and w.lower() not in STOP]

def frequencies(token_lists):
    c = Counter(t for toks in token_lists for t in toks)
    m = max(c.values()) if c else 1
    return {k: v / m for k, v in c.items()}  # normalized word frequency
