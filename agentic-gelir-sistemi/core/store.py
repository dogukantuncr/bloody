"""SQLite hafıza katmanı — tek dosya veritabanı, sunucu gerektirmez."""
import os
import json
import sqlite3
from datetime import datetime, timezone

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_ROOT, "data", "leads.db")
SCHEMA_PATH = os.path.join(_ROOT, "db", "schema.sql")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c, open(SCHEMA_PATH, encoding="utf-8") as f:
        c.executescript(f.read())


def upsert_lead(title, source, score, reason, skills):
    with _conn() as c:
        c.execute(
            "INSERT INTO leads(title, source, score, reason, skills, status, created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (title, source, score, reason,
             json.dumps(skills, ensure_ascii=False),
             "queued", datetime.now(timezone.utc).isoformat()),
        )


def top_leads(limit=50):
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM leads ORDER BY score DESC, created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
