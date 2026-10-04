import os, sqlite3
DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database.db")

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS summaries(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, original_text TEXT NOT NULL,
            summary TEXT NOT NULL, original_word_count INTEGER NOT NULL, summary_word_count INTEGER NOT NULL,
            summary_type TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')))""")

def add(title, text, summary, ow, sw, stype):
    init_db()
    with conn() as c:
        return c.execute("INSERT INTO summaries(title,original_text,summary,original_word_count,summary_word_count,summary_type) VALUES(?,?,?,?,?,?)",
                         (title, text, summary, ow, sw, stype)).lastrowid

def listing(q="", stype=""):
    init_db()
    sql, args = "SELECT id,title,summary,original_word_count,summary_word_count,summary_type,created_at FROM summaries WHERE 1=1", []
    if q: sql += " AND (title LIKE ? OR summary LIKE ? OR original_text LIKE ?)"; args += [f"%{q}%"] * 3
    if stype: sql += " AND summary_type=?"; args.append(stype)
    with conn() as c: return [dict(r) for r in c.execute(sql + " ORDER BY id DESC", args)]

def get(i):
    init_db()
    with conn() as c:
        r = c.execute("SELECT * FROM summaries WHERE id=?", (i,)).fetchone(); return dict(r) if r else None

def delete(i):
    init_db()
    with conn() as c: return c.execute("DELETE FROM summaries WHERE id=?", (i,)).rowcount > 0

def stats():
    init_db()
    with conn() as c:
        t = c.execute("""SELECT COUNT(*) n, COALESCE(SUM(original_word_count),0) words,
            COALESCE(AVG(summary_word_count),0) avg_len,
            COALESCE(AVG(100.0*(1-1.0*summary_word_count/original_word_count)),0) avg_comp FROM summaries""").fetchone()
        over = c.execute("SELECT date(created_at) d, COUNT(*) n FROM summaries GROUP BY d ORDER BY d").fetchall()
        types = c.execute("SELECT summary_type t, COUNT(*) n FROM summaries GROUP BY t").fetchall()
    return {"total_summaries": t["n"], "total_words": t["words"], "avg_summary_length": round(t["avg_len"], 1),
            "avg_compression": round(t["avg_comp"], 1),
            "over_time": [{"date": r["d"], "count": r["n"]} for r in over],
            "by_type": {r["t"]: r["n"] for r in types}}
