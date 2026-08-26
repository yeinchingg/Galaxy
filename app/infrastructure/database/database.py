# app/infrastructure/database.py
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from passlib.context import CryptContext

# 指向專案根目錄下的 astro_platform.db
DB_PATH = Path(__file__).resolve().parent.parent.parent / "astro_platform.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schema.sql"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    if SCHEMA_PATH.exists():
        with get_conn() as conn:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

# ------------------------------------------------------------------
# USERS
# ------------------------------------------------------------------


def create_user(username: str, password: str | None, role_type: str) -> int:
    password_hash = pwd_context.hash(password) if password else None
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, role_type) VALUES (?, ?, ?)",
            (username, password_hash, role_type),
        )
        return cur.lastrowid


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def verify_password(username: str, password: str) -> sqlite3.Row | None:
    user = get_user_by_username(username)
    if not user or not user["password_hash"]:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user

# ------------------------------------------------------------------
# SESSIONS / MESSAGES (對話紀錄)
# ------------------------------------------------------------------


def start_session(user_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO sessions (user_id) VALUES (?)", (user_id,))
        return cur.lastrowid


def save_message(session_id: int, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def get_chat_history(user_id: int, limit: int = 50):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT m.id, m.role, m.content, m.ts
               FROM messages m
               JOIN sessions s ON m.session_id = s.session_id
               WHERE s.user_id = ?
               ORDER BY m.ts DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_message(message_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            """DELETE FROM messages
               WHERE id = ? AND session_id IN (
                   SELECT session_id FROM sessions WHERE user_id = ?
               )""",
            (message_id, user_id),
        )
        return cur.rowcount > 0


def clear_chat_history(user_id: int):
    with get_conn() as conn:
        conn.execute(
            """DELETE FROM messages WHERE session_id IN (
                   SELECT session_id FROM sessions WHERE user_id = ?
               )""",
            (user_id,),
        )

# ------------------------------------------------------------------
# QUIZ SCORES (測驗成績紀錄，對應 profile 頁面)
# ------------------------------------------------------------------


def save_quiz_score(user_id: int, quiz_type: str, score: int, total_questions: int = 10) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO quiz_scores (user_id, quiz_type, score, total_questions)
               VALUES (?, ?, ?, ?)""",
            (user_id, quiz_type, score, total_questions),
        )
        return cur.lastrowid


def get_quiz_history(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM quiz_scores WHERE user_id = ?
               ORDER BY completed_at DESC""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
