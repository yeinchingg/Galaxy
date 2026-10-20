import json
from typing import List, Dict, Any, Optional
from app.domain.interfaces.repository_interface import IDataRepository
import os
from pathlib import Path
from app.infrastructure.database.database import get_conn, pwd_context

DATABASE_URL = os.getenv("DATABASE_URL")
from app.infrastructure.database.database import init_db

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "astro_platform.db"


class SQLiteRepository(IDataRepository):
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        init_db()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        with get_conn() as conn:
            cursor = conn.execute(
                """SELECT role, content FROM messages 
                   WHERE session_id = ? ORDER BY id ASC""",
                (session_id,),
            )
            rows = cursor.fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in rows]

    def save_message(
        self, session_id: str, role: str, content: str, user_id: int = 1
    ) -> None:
        with get_conn() as conn:
            cursor = conn.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?", (session_id,)
            )
            if not cursor.fetchone():
                try:
                    conn.execute(
                        "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
                        (session_id, user_id),
                    )
                except Exception:
                    conn.execute(
                        "INSERT INTO sessions (user_id) VALUES (?)", (user_id,)
                    )

            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def get_chat_history(self, user_id: int) -> List[Dict[str, Any]]:
        with get_conn() as conn:
            cursor = conn.execute(
                """SELECT m.id, m.session_id, m.role, m.content, m.ts
                   FROM messages m
                   JOIN sessions s ON s.session_id = m.session_id
                   WHERE s.user_id = ?
                   ORDER BY m.id ASC""",
                (user_id,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_message(self, message_id: int, user_id: int) -> bool:
        with get_conn() as conn:
            cur = conn.execute(
                """DELETE FROM messages
                   WHERE id = ?
                   AND session_id IN (
                       SELECT session_id FROM sessions WHERE user_id = ?
                   )""",
                (message_id, user_id),
            )
            return cur.rowcount > 0

    def clear_chat_history(self, user_id: int) -> None:
        with get_conn() as conn:
            conn.execute(
                """DELETE FROM messages
                   WHERE session_id IN (
                       SELECT session_id FROM sessions WHERE user_id = ?
                   )""",
                (user_id,),
            )
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

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
            if conn.is_pg:
                cur = conn.execute(
                    """INSERT INTO quiz_scores (user_id, quiz_type, score, total_questions)
                       VALUES (?, ?, ?, ?) RETURNING score_id""",
                    (user_id, quiz_type, score, total_questions),
                )
                return cur.fetchone()["score_id"]
            else:
                cur = conn.execute(
                    """INSERT INTO quiz_scores (user_id, quiz_type, score, total_questions)
                       VALUES (?, ?, ?, ?)""",
                    (user_id, quiz_type, score, total_questions),
                )
                return cur.lastrowid

    def get_quiz_history(self, user_id: int):
        with get_conn() as conn:
            cursor = conn.execute(
                """SELECT * FROM quiz_scores WHERE user_id = ?
                   ORDER BY completed_at DESC""",
                (user_id,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def clear_quiz_history(self, user_id: int) -> None:
        with get_conn() as conn:
            conn.execute("DELETE FROM quiz_scores WHERE user_id = ?", (user_id,))

    def delete_quiz_score(self, score_id: int, user_id: int) -> bool:
        with get_conn() as conn:
            cur = conn.execute(
                "DELETE FROM quiz_scores WHERE score_id = ? AND user_id = ?",
                (score_id, user_id),
            )
            return cur.rowcount > 0


def create_user(username: str, password: str | None, role_type: str) -> int:
    password_hash = pwd_context.hash(password) if password else None
    with get_conn() as conn:
        if conn.is_pg:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role_type) VALUES (?, ?, ?) RETURNING user_id",
                (username, password_hash, role_type),
            )
            return cur.fetchone()["user_id"]
        else:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role_type) VALUES (?, ?, ?)",
                (username, password_hash, role_type),
            )
            return cur.lastrowid


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None


def verify_password(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_username(username)
    if not user or not user.get("password_hash"):
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user
