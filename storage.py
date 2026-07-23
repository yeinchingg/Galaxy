# storage.py
"""
用 SQLite 儲存兩種資料：
1. interactions：使用者在介面上的操作紀錄（點了哪個主題、調了哪個參數），
   用來動態產生「今晚課程大綱」的推薦排序。
2. messages：對話紀錄，依 session_id 儲存/讀取。

SQLite 檔案在正式環境建議換成 Postgres，但介面/呼叫方式可以完全不變，
之後要換資料庫只需要改這支檔案。
"""

import sqlite3
import json
import time
import uuid
from contextlib import contextmanager

DB_PATH = "astro_platform.db"


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                action TEXT NOT NULL,
                params_json TEXT,
                ts REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                ts REAL NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")


# ---------- 使用者互動紀錄（課程大綱用） ----------

def log_interaction(user_id: str, topic: str, action: str, params: dict | None = None):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO interactions (user_id, topic, action, params_json, ts) VALUES (?, ?, ?, ?, ?)",
            (user_id, topic, action, json.dumps(
                params or {}, ensure_ascii=False), time.time()),
        )


def get_recent_interactions(user_id: str, limit: int = 50) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT topic, action, params_json, ts FROM interactions WHERE user_id = ? ORDER BY ts DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [
            {"topic": r["topic"], "action": r["action"],
             "params": json.loads(r["params_json"]), "ts": r["ts"]}
            for r in rows
        ]


# ---------- 對話紀錄 ----------

def new_session_id() -> str:
    return str(uuid.uuid4())


def save_message(session_id: str, role: str, content: str):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, ts) VALUES (?, ?, ?, ?)",
            (session_id, role, content, time.time()),
        )


def get_history(session_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, ts FROM messages WHERE session_id = ? ORDER BY ts ASC",
            (session_id,),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"], "ts": r["ts"]} for r in rows]
