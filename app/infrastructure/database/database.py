"""
app/infrastructure/database/database.py

負責統一管理 SQLite 連線與所有資料表的讀寫邏輯。
所有跟資料庫互動的程式碼都應該只透過這支檔案存取，避免其他地方各自寫 SQL。

⚠️ 檔案位置注意：
本檔案實際路徑是 app/infrastructure/database/database.py（database 資料夾底下），
其他地方請一律用 `from app.infrastructure.database.database import ...` 來 import。
同資料夾底下必須有一個 __init__.py，否則 Python 找不到這個 package。
"""
import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Optional, Any

from passlib.context import CryptContext

from app.domain.interfaces import IDataRepository

# 專案根目錄下的 astro_platform.db
# 此檔案位於 app/infrastructure/database/database.py，往上四層才是專案根目錄
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "astro_platform.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@contextmanager
def get_conn():
    """單一次資料庫連線的 context manager，離開 with 區塊時自動 commit 並關閉連線。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """自動建立所有資料表（若不存在），並確保有一個預設的訪客帳號 (user_id = 1)。"""
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
    """對應 Clean Architecture 的 Infrastructure 層，實作 IDataRepository 介面。"""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        init_db()

    # ---------- 聊天紀錄 ----------

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in rows]

    def _ensure_session(self, conn: sqlite3.Connection, session_id: str, user_id: int) -> None:
        """若 session 尚未存在就建立一筆，並帶入正確的 user_id。"""
        row = conn.execute(
            "SELECT session_id FROM sessions WHERE session_id = ?", (
                session_id,)
        ).fetchone()
        if row:
            return
        try:
            conn.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
                (session_id, user_id),
            )
        except sqlite3.OperationalError:
            # 相容舊版 schema：若 sessions 表沒有 session_id 欄位，退回自動編號模式
            conn.execute(
                "INSERT INTO sessions (user_id) VALUES (?)", (user_id,))

    def save_message(self, session_id: str, role: str, content: str, user_id: int = 1) -> None:
        """
        寫入一筆訊息。

        修正說明：原本這裡有兩段幾乎一樣的邏輯（可能是合併程式碼時忘記刪舊版），
        導致每呼叫一次就把同一則訊息寫進資料庫「兩次」，而且第二段還把 user_id
        寫死成 1（訪客帳號），跟傳進來的真正 user_id 互相矛盾。
        現在合併成一段，只寫入一次，且正確使用傳入的 user_id。
        """
        with get_conn() as conn:
            self._ensure_session(conn, session_id, user_id)
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> None:
        for msg in history:
            self.save_message(session_id, msg.get(
                "role", "user"), msg.get("content", ""))

    def log_interaction(
        self, user_id: Any, topic: str, action: str, params: Optional[dict] = None
    ) -> None:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO interactions (user_id, topic, action, params_json) VALUES (?, ?, ?, ?)",
                (user_id, topic, action, json.dumps(
                    params or {}, ensure_ascii=False)),
            )

    # ---------- 測驗紀錄 ----------

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

    def get_quiz_history(self, user_id: int) -> List[Dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM quiz_scores WHERE user_id = ? ORDER BY completed_at DESC",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]


# ---------- 使用者帳號（給 auth_controller 使用） ----------

def create_user(username: str, password: Optional[str], role_type: str) -> int:
    password_hash = pwd_context.hash(password) if password else None
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, role_type) VALUES (?, ?, ?)",
            (username, password_hash, role_type),
        )
        return cur.lastrowid


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def verify_password(username: str, password: str) -> Optional[sqlite3.Row]:
    user = get_user_by_username(username)
    if not user or not user["password_hash"]:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user
