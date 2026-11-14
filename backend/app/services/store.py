"""Saves sessions, items and turns to SQLite (ARCHITECTURE.md 3.8). No personal data."""
from contextlib import closing
from datetime import datetime, timezone
import json
import sqlite3
import uuid

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, learner_level TEXT, explain_lang TEXT);
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY, session_id TEXT REFERENCES sessions(id), case_id TEXT,
    intended_meaning TEXT, status TEXT, tier INTEGER, solved_at_tier INTEGER,
    sources_json TEXT, retrieval_json TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT REFERENCES items(id), n INTEGER,
    event TEXT, learner_text TEXT, tier INTEGER, verdict_json TEXT, response_json TEXT,
    prompt_json TEXT, raw_output TEXT, guard_json TEXT, level_json TEXT, warnings_json TEXT,
    model TEXT, model_digest TEXT, seed INTEGER, eval_count INTEGER, timing_json TEXT,
    created_at TEXT);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id():
    return uuid.uuid4().hex


def to_json(value):
    return None if value is None else json.dumps(value, ensure_ascii=False)


def init_db(db_path):
    """Create the folder and the 3 tables if they don't exist yet. Safe to run every start."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as db:
        db.executescript(SCHEMA)


def log_ask(db_path, *, question, level, explain_lang, sources, retrieval, result, timing):
    """Save one /api/ask as 1 session + 1 item + 1 turn. Returns the item id."""
    session_id, item_id, created = new_id(), new_id(), now()
    with closing(sqlite3.connect(db_path)) as db:
        with db:  # one transaction: all 3 rows are saved, or none
            db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
                (session_id, created, "ask", level, explain_lang))
            db.execute(
                """INSERT INTO items (id, session_id, intended_meaning, status,
                       sources_json, retrieval_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (item_id, session_id, question, "answered",
                 to_json(sources), to_json(retrieval), created))
            db.execute(
                """INSERT INTO turns (item_id, n, event, learner_text, response_json,
                       prompt_json, raw_output, warnings_json, model, model_digest,
                       eval_count, timing_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item_id, 1, "ask", question,
                 to_json({"answer": result["answer"], "truncated": result["truncated"]}),
                 to_json(result["messages"]), result["raw_output"],
                 to_json(result["warnings"]), result["model"], result["model_digest"],
                 result["eval_count"], to_json(timing), created))
    return item_id