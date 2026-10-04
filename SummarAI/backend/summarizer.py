"""Extractive (TF-IDF + frequency + position, redundancy-aware) and optional abstractive summarization."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from . import nlp_processor as nlp
from .utils import LENGTHS

def _norm(a):
    a = np.asarray(a, float); r = a.max() - a.min()
    return (a - a.min()) / r if r else np.zeros_like(a)

def extractive(text, length="medium"):
    sents = nlp.sentences(nlp.clean_text(text))
    n = len(sents)
    toks = [nlp.content_tokens(s) for s in sents]
    freq = nlp.frequencies(toks)
    if not freq: return {"summary": " ".join(sents[:2]), "selected": min(2, n), "keywords": []}
    M = TfidfVectorizer(analyzer=lambda x: x).fit_transform(toks)  # tokens already preprocessed
    tfidf = np.asarray(M.sum(axis=1)).ravel() / np.maximum(1, np.diff(M.indptr))
    fscore = [sum(freq[t] for t in tk) / len(tk) if tk else 0 for tk in toks]
    pos = [1.0 if i == 0 else 0.5 if i == n - 1 else 0.0 for i in range(n)]
    score = 0.5 * _norm(tfidf) + 0.35 * _norm(fscore) + 0.15 * np.array(pos)
    score = np.array([s * (0.5 if len(tk) < 5 else 1) for s, tk in zip(score, toks)])  # penalize fragments
    k = max(1, round(n * LENGTHS[length]))
    sim, chosen = cosine_similarity(M), []
    for i in np.argsort(-score):  # best first, skipping near-duplicates
        if all(sim[i, j] < 0.6 for j in chosen): chosen.append(int(i))
        if len(chosen) == k: break
    chosen.sort()  # keep original order for readability
    surface = {}
    for s in sents:
        for w in nlp.words(s):
            surface.setdefault(nlp.stemmer.stem(w.lower()), w.lower())
    kws = [surface.get(t, t) for t in sorted(freq, key=freq.get, reverse=True)[:8]]
    return {"summary": " ".join(sents[i] for i in chosen), "selected": len(chosen), "keywords": kws}

_pipe = None
def abstractive(text, length="medium"):
    """Optional transformer summarizer; raises if transformers/model is unavailable."""
    global _pipe
    from transformers import pipeline
    if _pipe is None: _pipe = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    ws, out = text.split(), []
    mx = {"short": 60, "medium": 110, "detailed": 180}[length]
    for i in range(0, len(ws), 600):
        out.append(_pipe(" ".join(ws[i:i + 600]), max_length=mx, min_length=20, truncation=True)[0]["summary_text"])
    s = " ".join(out)
    return {"summary": s, "selected": len(nlp.sentences(s)), "keywords": []}

def summarize(text, length="medium", mode="extractive"):
    note = ""
    if mode == "abstractive":
        try:
            r = abstractive(text, length); r.update(mode="abstractive", note=""); return r
        except Exception:
            note = "The abstractive model is not available, so the extractive method was used instead."
    r = extractive(text, length); r.update(mode="extractive", note=note)
    return r
