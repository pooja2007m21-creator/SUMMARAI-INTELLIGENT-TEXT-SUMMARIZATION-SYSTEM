# SummarAI – Intelligent Text Summarization System

A full-stack NLP web app for the **Text and Speech Analysis** subject. It turns long text into concise summaries using TF-IDF-based sentence scoring, stores results in SQLite, and shows usage analytics.

> **Note:** Automated summaries may omit context or contain errors. Review them before using them for important academic or professional work.

## Problem statement
Reading long articles, notes and reports is slow. Users need a quick, reviewable condensed version that keeps the main points.

## Objective
Build a working summarizer that selects the most informative sentences from user-supplied text (extractive) and optionally rewrites them with a transformer model (abstractive).

## Features
Text editor with live word/character/sentence counts · Short/Medium/Detailed lengths · Side-by-side original and summary (stacked on mobile) · Compression and sentence statistics · Copy and download · History with search, filters, view, copy, delete · Analytics dashboard with Chart.js · Dark/light mode · Validation and friendly errors.

## Technology stack
HTML5, CSS3, vanilla JS · Python, Flask (REST) · NLTK, scikit-learn · SQLite · Chart.js (CDN) · optional `transformers`.

## NLP workflow
Text → cleaning → sentence tokenization → word tokenization → stop-word removal and stemming → word frequencies → TF-IDF per sentence → sentence score (0.5 TF-IDF + 0.35 frequency + 0.15 position bonus; short fragments penalized) → top-k selection with cosine-similarity redundancy filter → sentences restored to original order.
`k` = 15% (short), 30% (medium) or 50% (detailed) of the sentences, minimum 1.

## System architecture
Browser (HTML/JS) → Flask REST API (`routes.py`) → `summarizer.py` + `nlp_processor.py` → SQLite (`database.py`). Flask also serves the pages.

## Project structure
```text
SummarAI/
├── app.py  requirements.txt  README.md  .gitignore  (database.db is created on first run)
├── backend/   database.py routes.py summarizer.py nlp_processor.py utils.py
├── frontend/  index/summarize/history/analytics/about .html, css/style.css, js/*.js
└── static/assets/
```

## Installation
```bash
python -m venv venv
venv\Scripts\activate        # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
NLTK data (`punkt`, `punkt_tab`, `stopwords`) downloads automatically on first run. If you are offline, built-in fallbacks are used (regex tokenizer and a basic stop-word list), and results may be slightly less accurate.

Optional abstractive mode: `pip install transformers torch` (downloads a model of several hundred MB on first use). If unavailable, the app falls back to extractive and says so.

## How to run
```bash
python app.py
```
Open http://127.0.0.1:5000

## API documentation
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/summarize` | Body: `{"title","text","length":"short\|medium\|detailed","mode":"extractive\|abstractive"}` → summary, counts, compression, key terms |
| GET | `/api/history?q=&type=` | List summaries (search and filter) |
| GET | `/api/history/<id>` | One summary with original text |
| DELETE | `/api/history/<id>` | Delete a summary |
| GET | `/api/stats` | Totals, averages, time series, type distribution |
| GET | `/api/health` | `{"status":"ok"}` |

Errors return `{"error": "<friendly message>"}` with a 4xx/5xx status; stack traces are never sent to the client.
Validation: empty text, fewer than 30 words, more than 100,000 characters, bad length/mode, non-JSON body.

## Database
SQLite table `summaries`: `id, title, original_text, summary, original_word_count, summary_word_count, summary_type, created_at`.

## Limitations
Extractive output can read choppily and lose context; tuned for English; quality varies with text type; abstractive output can contain factual errors; no accuracy score is shown because none can be computed without a reference summary.

## Future enhancements
Multi-language support, PDF/URL input, ROUGE evaluation, user accounts, speech-to-text input, keyword highlighting.
