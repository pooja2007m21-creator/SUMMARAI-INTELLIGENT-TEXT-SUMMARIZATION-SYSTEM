import re
from flask import jsonify

MIN_WORDS, MAX_CHARS = 30, 100_000
LENGTHS = {"short": 0.15, "medium": 0.30, "detailed": 0.50}

def word_count(t): return len(re.findall(r"\b[\w'-]+\b", t or ""))

def error(msg, code=400): return jsonify(error=msg), code

def validate(data):
    """Return (clean_payload, error_message)."""
    if not isinstance(data, dict): return None, "Invalid request. Send JSON with a 'text' field."
    text, title = data.get("text"), data.get("title") or ""
    length, mode = data.get("length", "medium"), data.get("mode", "extractive")
    if not isinstance(text, str) or not text.strip(): return None, "Please enter some text to summarize."
    if not isinstance(title, str): return None, "Title must be text."
    if length not in LENGTHS: return None, "Length must be short, medium or detailed."
    if mode not in ("extractive", "abstractive"): return None, "Mode must be extractive or abstractive."
    if len(text) > MAX_CHARS: return None, f"Text is too long. Please keep it under {MAX_CHARS:,} characters."
    if word_count(text) < MIN_WORDS: return None, f"Text is too short to summarize. Enter at least {MIN_WORDS} words."
    return {"text": text.strip(), "title": title.strip()[:150] or "Untitled", "length": length, "mode": mode}, None
