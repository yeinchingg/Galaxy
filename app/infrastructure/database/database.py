# app/infrastructure/database.py
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from passlib.context import CryptContext
from app.domain.interfaces import IDataRepository
from typing import List, Dict, Optional, Any

# 指向專案根目錄下的 astro_platform.db
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "astro_platform.db"

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
    """自動建立所有資料表與預設訪客身分"""
    with get_conn() as conn:
        conn.executescript(
            """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            role_type TEXT NOT NULL DEFAULT 'registered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO users (user_id, username, role_type) 
        VALUES (1, 'guest_user', 'guest');

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            action TEXT NOT NULL,
            params_json TEXT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS quiz_scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_type TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL DEFAULT 10,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        )


class SQLiteRepository(IDataRepository):
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        init_db()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT role, content FROM messages 
                   WHERE session_id = ? ORDER BY id ASC""",
                (session_id,),
            ).fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in rows]

    def save_message(self, session_id: str, role: str, content: str) -> None:
        with get_conn() as conn:
            cursor = conn.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?", (session_id,)
            )
            if not cursor.fetchone():
                try:
                    conn.execute(
                        "INSERT INTO sessions (session_id, user_id) VALUES (?, 1)",
                        (session_id,),
                    )
                except sqlite3.OperationalError:
                    conn.execute("INSERT INTO sessions (user_id) VALUES (1)")

            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> None:
        for msg in history:
            self.save_message(
                session_id, msg.get("role", "user"), msg.get("content", "")
            )

    def log_interaction(
        self, user_id: Any, topic: str, action: str, params: dict | None = None
    ):
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO interactions (user_id, topic, action, params_json) VALUES (?, ?, ?, ?)",
                (user_id, topic, action, json.dumps(params or {}, ensure_ascii=False)),
            )

    def save_quiz_score(
        self, user_id: int, quiz_type: str, score: int, total_questions: int = 10
    ) -> int:
        with get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO quiz_scores (user_id, quiz_type, score, total_questions)
                   VALUES (?, ?, ?, ?)""",
                (user_id, quiz_type, score, total_questions),
            )
            return cur.lastrowid

    def get_quiz_history(self, user_id: int):
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM quiz_scores WHERE user_id = ?
                   ORDER BY completed_at DESC""",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]


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
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def verify_password(username: str, password: str) -> sqlite3.Row | None:
    user = get_user_by_username(username)
    if not user or not user["password_hash"]:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user
