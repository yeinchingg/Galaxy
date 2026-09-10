"""
app/adapters/controllers/chat_controller.py
Clean Architecture - Controller / Adapter 層
負責處理前端發起的所有 API 請求（AI 聊天、新聞、測驗紀錄、行為追蹤、歷史對話、星空觀測歷程）
"""

import os
import requests
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.use_cases.rag_chat_use_case import RAGChatUseCase
from app.infrastructure.database import database as db

router = APIRouter()
_use_case: Optional[RAGChatUseCase] = None
_db_repo = None  # 資料庫 Repo


def set_use_case(use_case: RAGChatUseCase):
    global _use_case
    _use_case = use_case
    if hasattr(use_case, "session_repo"):
        global _db_repo
        _db_repo = use_case.session_repo


# ---------------- Schema 定義 ----------------
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 3
    user_id: Optional[int] = 1


class GuestLoginRequest(BaseModel):
    display_name: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class NarrateRequest(BaseModel):
    context_description: str


class TrackRequest(BaseModel):
    user_id: str
    topic: str
    action: str
    params: Dict[str, Any] = {}


class QuizScoreRequest(BaseModel):
    user_id: int
    quiz_type: str
    score: int
    total_questions: int = 10


class BodyLogRequest(BaseModel):
    name: str
    body_type: str
    alt: Optional[float] = None
    az: Optional[float] = None
    mag: Optional[float] = None
    user_id: Optional[str] = "1"


# ---------------- 備援新聞池 ----------------
NEWS_FALLBACK_POOL = [
    {
        "title": "韋伯太空望遠鏡發現早期遙遠星系新線索",
        "sub_title": "天文學家透過最新觀測數據，揭示了宇宙大爆炸後數億年內星系快速演化的秘密與結構。",
        "image_url": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=500&auto=format&fit=crop&q=80",
        "url": "https://www.nasa.gov/mission_pages/webb/main/index.html",
    },
    {
        "title": "哈伯望遠鏡捕捉到精美螺旋星系動態",
        "sub_title": "這顆位於深空中的星系展現出清晰的旋臂結構，提供恆星誕生速率的重要研究依據。",
        "image_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=500&auto=format&fit=crop&q=80",
        "url": "https://nasa.gov/hubble",
    },
    {
        "title": "探討系外行星大氣中的生物標記與適居性",
        "sub_title": "科學家利用高解析光譜分析技術，進一步評估多個類地行星尋找生命跡象的可能性。",
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
        "url": "https://exoplanets.nasa.gov/",
    },
]


# ---------------- API 端點 ----------------


@router.get("/status")
def get_system_status():
    """系統連線與 AI 模組狀態檢測"""
    return {
        "status": "online",
        "service": "StarLearn Astro Platform",
        "ai_ready": _use_case is not None,
    }


@router.post("/auth/guest")
def auth_guest(req: GuestLoginRequest):
    """訪客登入"""
    display_name = (req.display_name or "訪客研究員").strip() or "訪客研究員"
    unique_username = f"guest_{os.urandom(4).hex()}"
    user_id = db.create_user(unique_username, password=None, role_type="guest")
    return {
        "user_id": user_id,
        "username": display_name,
        "role": "guest",
    }


@router.post("/auth/register")
def auth_register(req: RegisterRequest):
    """建立會員帳號"""
    username = req.username.strip()
    password = req.password.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="帳號與密碼不能為空")

    if db.get_user_by_username(username):
        raise HTTPException(status_code=409, detail="這個使用者名稱已經被註冊了")

    try:
        user_id = db.create_user(username, password=password, role_type="member")
    except Exception as e:
        print(f"❌ [DB] 建立帳號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"建立帳號失敗：{e}")

    return {
        "user_id": user_id,
        "username": username,
        "role": "member",
    }


@router.post("/auth/login")
def auth_login(req: LoginRequest):
    """帳號密碼登入"""
    username = req.username.strip()
    password = req.password.strip()
    user = db.verify_password(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role_type"],
    }


@router.get("/news")
def get_news(limit: int = 6):
    """即時太空新聞端點"""
    news_items = []
    try:
        url = f"https://api.spaceflightnewsapi.net/v4/articles/?limit={limit}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            results = res.json().get("results", [])
            for item in results:
                news_items.append(
                    {
                        "title": item.get("title", "無標題"),
                        "sub_title": (item.get("summary", "") or "")[:110] + "...",
                        "image_url": item.get("image_url")
                        or "https://via.placeholder.com/300x180",
                        "url": item.get("url", "#"),
                    }
                )
    except Exception as e:
        print(f"⚠️ 抓取 Spaceflight News 失敗 ({e})，啟動降級備援...")

    if len(news_items) < 2:
        news_items = NEWS_FALLBACK_POOL

    return news_items


@router.get("/daily-knowledge")
def get_daily_knowledge():
    """相容舊版路由的每日新聞"""
    return {"status": "success", "data": get_news(4)}


# --- 測驗成績相關端點 ---
@router.post("/quiz/score")
def save_quiz_score(req: QuizScoreRequest):
    if not _db_repo:
        raise HTTPException(status_code=500, detail="資料庫 Repo 尚未初始化")

    try:
        score_id = _db_repo.save_quiz_score(
            req.user_id, req.quiz_type, req.score, req.total_questions
        )
        return {"status": "success", "score_id": score_id}
    except Exception as e:
        print(f"❌ [DB] 儲存測驗成績出錯: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quiz/history/{user_id}")
def get_quiz_history(user_id: int):
    if not _db_repo:
        raise HTTPException(status_code=500, detail="資料庫 Repo 尚未初始化")
    return _db_repo.get_quiz_history(user_id)


@router.delete("/quiz/history/{user_id}")
def clear_quiz_history(user_id: int):
    if not _db_repo:
        raise HTTPException(status_code=500, detail="資料庫 Repo 尚未初始化")
    if hasattr(_db_repo, "clear_quiz_history"):
        _db_repo.clear_quiz_history(user_id)
        return {"status": "success"}
    return {"status": "error", "message": "功能未支援"}


@router.delete("/quiz/score/{score_id}")
def delete_quiz_score(score_id: int, user_id: int = 1):
    if not _db_repo:
        raise HTTPException(status_code=500, detail="資料庫 Repo 尚未初始化")
    if hasattr(_db_repo, "delete_quiz_score"):
        success = _db_repo.delete_quiz_score(score_id, user_id)
        return {"status": "success", "deleted": success}
    return {"status": "error", "message": "功能未支援"}


# --- 聊天與 AI 相關端點 ---
@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")
    return _use_case.ask(req.question, top_k=req.top_k or 3, session_id=req.session_id)


@router.post("/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")

    session_id = req.session_id or f"session_{os.urandom(4).hex()}"

    def sse_event_generator():
        yield f"event: session\ndata: {session_id}\n\n"
        full_answer = []
        try:
            stream_gen = _use_case.generate_stream(
                req.question, top_k=req.top_k or 3, session_id=session_id
            )
            for chunk in stream_gen:
                if chunk:
                    full_answer.append(chunk)
                    yield f"data: {chunk}\n\n"
        except Exception as e:
            print(f"❌ [API] AI 串流生成出錯: {e}")
            yield f"data: (AI 助理遇到暫時性問題: {str(e)})\n\n"

        if _db_repo:
            try:
                uid = req.user_id or 1
                _db_repo.save_message(session_id, "user", req.question, user_id=uid)
                _db_repo.save_message(
                    session_id, "assistant", "".join(full_answer), user_id=uid
                )
            except Exception as db_err:
                print(f"❌ [DB] 寫入資料庫失敗: {db_err}")

        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/history")
def get_chat_history_endpoint(user_id: int = 1):
    if not _db_repo:
        raise HTTPException(status_code=500, detail="資料庫 Repo 尚未初始化")
    if hasattr(_db_repo, "get_chat_history"):
        return _db_repo.get_chat_history(user_id)
    return []


@router.delete("/chat/message/{message_id}")
def delete_chat_message(message_id: int, user_id: int = 1):
    if _db_repo and hasattr(_db_repo, "delete_message"):
        success = _db_repo.delete_message(message_id, user_id)
        return {"status": "success", "deleted": success}
    return {"status": "error", "message": "功能未支援"}


@router.delete("/chat/history")
def clear_all_chat_history(user_id: int = 1):
    if _db_repo and hasattr(_db_repo, "clear_chat_history"):
        _db_repo.clear_chat_history(user_id)
        return {"status": "success"}
    return {"status": "error", "message": "功能未支援"}


@router.post("/3d/narrate")
def narrate_endpoint(req: NarrateRequest):
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")
    hint = _use_case.generate_short_hint(req.context_description)
    return {"hint": hint}


@router.post("/track")
def track_user_action(req: TrackRequest):
    if _db_repo and hasattr(_db_repo, "log_interaction"):
        _db_repo.log_interaction(req.user_id, req.topic, req.action, req.params)
    return {"status": "tracked"}


@router.get("/outline/{user_id}")
def get_outline(user_id: str):
    return {
        "status": "success",
        "user_id": user_id,
        "outline": [
            {
                "topic": "stellar_evolution",
                "title": "恆星演化史與赫羅圖",
                "visit_count": 3,
            },
            {"topic": "black_hole", "title": "黑洞物理與重力透鏡", "visit_count": 1},
        ],
    }


# --- 星空觀測儀端點 ---
@router.post("/sky/observe")
def log_celestial_observation(req: BodyLogRequest):
    """紀錄觀測行為至資料庫，毫秒級回應，不進行慢速 AI 語音處理"""
    if _db_repo and hasattr(_db_repo, "log_interaction"):
        try:
            _db_repo.log_interaction(
                user_id=req.user_id or "1",
                topic="sky_observatory",
                action="observe_target",
                params={
                    "target_name": req.name,
                    "type": req.body_type,
                    "altitude": req.alt,
                    "azimuth": req.az,
                    "mag": req.mag,
                },
            )
        except Exception as e:
            print(f"⚠️ 觀測紀錄寫入失敗: {e}")

    return {"status": "success", "target": req.name}
