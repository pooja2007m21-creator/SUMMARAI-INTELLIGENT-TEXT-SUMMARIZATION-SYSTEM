import time
from flask import Blueprint, jsonify, request
from . import database as db
from . import nlp_processor as nlp
from .summarizer import summarize
from .utils import validate, word_count, error

api = Blueprint("api", __name__)

@api.get("/health")
def health(): return jsonify(status="ok")

@api.post("/summarize")
def do_summarize():
    data, err = validate(request.get_json(silent=True))
    if err: return error(err)
    t0 = time.time()
    try:
        r = summarize(data["text"], data["length"], data["mode"])
    except Exception:
        return error("The text could not be processed. Please check it and try again.", 500)
    ow, sw = word_count(data["text"]), word_count(r["summary"])
    osent = len(nlp.sentences(nlp.clean_text(data["text"])))
    sid = db.add(data["title"], data["text"], r["summary"], ow, sw, data["length"])
    return jsonify(status="Summary generated successfully.", id=sid, summary=r["summary"], mode=r["mode"],
                   note=r["note"], keywords=r["keywords"], original_words=ow, summary_words=sw,
                   original_sentences=osent, summary_sentences=r["selected"],
                   compression=round((1 - sw / ow) * 100, 1) if ow else 0, seconds=round(time.time() - t0, 2))

@api.get("/history")
def history():
    t = request.args.get("type", "")
    return jsonify(items=db.listing(request.args.get("q", "").strip(), t if t in ("short", "medium", "detailed") else ""))

@api.get("/history/<int:i>")
def history_one(i):
    r = db.get(i)
    return jsonify(r) if r else error("Summary not found.", 404)

@api.delete("/history/<int:i>")
def history_del(i):
    return jsonify(deleted=True) if db.delete(i) else error("Summary not found.", 404)

@api.get("/stats")
def stats(): return jsonify(db.stats())
