"""
app/infrastructure/database/sqlite_repository.py
SQLite 資料庫存取實作
"""

import sqlite3
from typing import List, Dict
from app.use_cases.interfaces import IDataRepository


class SQLiteRepository(IDataRepository):
    def __init__(self, db_path: str = "astro_platform.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]

    def save_message(self, session_id: str, role: str, content: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> None:
        for msg in history:
            self.save_message(session_id, msg.get("role", "user"), msg.get("content", ""))