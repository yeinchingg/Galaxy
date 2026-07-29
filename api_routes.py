# api_routes.py
"""
所有對外 API 路由統一集中在這裡管理。

main.py 只負責：
  1. 建立 FastAPI app / CORS
  2. 初始化 rag_engine / star_sim / storage 等「依賴物件」
  3. 呼叫 init_routes() 把依賴物件注入進來，再 include_router()

這支檔案只負責：
  1. 定義所有 /api/* 的路由與其對應的 Pydantic Schema
  2. 呼叫注入進來的 rag / star_sim / storage 完成商業邏輯
  3. 不主動 import main.py，避免循環匯入
"""

import collections
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api")

# ------------------------------------------------------------------
# 依賴注入（由 main.py 在啟動時呼叫 init_routes 填入）
# ------------------------------------------------------------------
rag = None
star_sim = None
storage = None


def init_routes(rag_engine, star_simulator, storage_module):
    """由 main.py 在建立好 rag_engine / star_sim / storage 之後呼叫一次。"""
    global rag, star_sim, storage
    rag = rag_engine
    star_sim = star_simulator
    storage = storage_module


def _ensure_ready():
    if rag is None or star_sim is None or storage is None:
        raise HTTPException(status_code=500, detail="API 尚未初始化，請確認 main.py 有呼叫 init_routes()")


# ====================================================================
# Schemas
# ====================================================================

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3
    session_id: Optional[str] = None


class TopicQuestionRequest(BaseModel):
    question: str
    topic: str = "chat"
    top_k: int = 3
    session_id: Optional[str] = None


class TrackRequest(BaseModel):
    user_id: str
    topic: str
    action: str
    params: dict = {}


class StarInitialRequest(BaseModel):
    mass: float
    metallicity: float = 1.0
    rotation: float = 0.0


class StarEvolveRequest(StarInitialRequest):
    age_gyr: float
    with_hint: bool = False
    user_id: Optional[str] = "demo_user"


class StreamChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    top_k: int = 3


class NarrateRequest(BaseModel):
    context_description: str


# ====================================================================
# 1. 智慧問答 (RAG)
# ====================================================================

@router.post("/ask")
def ask_astronomy(payload: QuestionRequest):
    _ensure_ready()
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    result = rag.ask(payload.question, top_k=payload.top_k, session_id=payload.session_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result


@router.post("/qa/topic")
def ask_topic(payload: TopicQuestionRequest):
    _ensure_ready()
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    result = rag.ask_topic(
        payload.question, payload.topic, top_k=payload.top_k, session_id=payload.session_id
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result


# ====================================================================
# 2. 對話紀錄 / 串流
# ====================================================================

@router.post("/chat/session")
def create_session():
    _ensure_ready()
    return {"status": "success", "session_id": storage.new_session_id()}


@router.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    _ensure_ready()
    return {"status": "success", "session_id": session_id, "messages": storage.get_history(session_id)}


@router.post("/chat/stream")
def chat_stream(payload: StreamChatRequest):
    _ensure_ready()
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    session_id = payload.session_id or storage.new_session_id()

    # 記憶要能生效，存訊息這件事必須發生在「產生這一輪回答之前」，
    # 這樣 rag._build_history_block 只會看到「先前」的訊息，不會重複看到這一輪。
    storage.save_message(session_id, "user", payload.question)

    def event_generator():
        retrieved = rag.retrieve_context(payload.question, top_k=payload.top_k)
        full_answer = []
        yield f"event: session\ndata: {session_id}\n\n"
        for chunk in rag.generate_stream(payload.question, retrieved, session_id=session_id):
            full_answer.append(chunk)
            yield f"data: {chunk}\n\n"

        # 串流結束後做輕量清理，避免存進 DB 的內容帶有多餘空白，
        # 汙染下一輪從 storage.get_history 撈出來的「記憶」內容。
        final_text = "".join(full_answer).strip()
        storage.save_message(session_id, "assistant", final_text)
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ====================================================================
# 3. 恆星模擬
# ====================================================================

@router.post("/star/initial")
def star_initial(payload: StarInitialRequest):
    _ensure_ready()
    return {
        "status": "success",
        "data": star_sim.compute_initial(payload.mass, payload.metallicity, payload.rotation),
    }


@router.post("/star/evolve")
def star_evolve(payload: StarEvolveRequest):
    _ensure_ready()

    # 紀錄使用者調整參數的操作，讓「今晚課程大綱」能反映恆星模擬的使用狀況
    storage.log_interaction(
        user_id=payload.user_id,
        topic="star_lifecycle",
        action="adjust_params",
        params=payload.model_dump(exclude={"user_id"}),
    )

    result = star_sim.evolve(payload.mass, payload.metallicity, payload.rotation, payload.age_gyr)
    response = {"status": "success", "data": result}

    if payload.with_hint:
        description = (
            f"質量{payload.mass}倍太陽、目前階段：{result['stage_name']}、"
            f"溫度約{result['current_temperature_k']}K"
        )
        response["hint"] = rag.generate_short_hint(description)

    return response


# ====================================================================
# 4. 3D 場景旁白
# ====================================================================

@router.post("/3d/narrate")
def narrate_3d(payload: NarrateRequest):
    _ensure_ready()
    hint = rag.generate_short_hint(payload.context_description)
    return {"status": "success", "hint": hint}


# ====================================================================
# 5. 使用者互動紀錄 + 動態課程大綱
# ====================================================================

STATIC_TOPICS = [
    {"topic": "physics_meaning", "title": "物理數據的意義"},
    {"topic": "star_lifecycle", "title": "恆星的一生"},
    {"topic": "chat", "title": "對話空間"},
    {"topic": "3d", "title": "3D 投影"},
]


@router.post("/track")
def track_interaction(payload: TrackRequest):
    _ensure_ready()
    storage.log_interaction(payload.user_id, payload.topic, payload.action, payload.params)
    return {"status": "success"}


@router.get("/outline/{user_id}")
def get_outline(user_id: str):
    _ensure_ready()
    interactions = storage.get_recent_interactions(user_id, limit=100)
    topic_counts = collections.Counter(i["topic"] for i in interactions)

    last_params_by_topic: dict[str, dict] = {}
    for i in interactions:
        if i["topic"] not in last_params_by_topic and i["params"]:
            last_params_by_topic[i["topic"]] = i["params"]

    outline = sorted(
        [dict(t) for t in STATIC_TOPICS],
        key=lambda t: topic_counts.get(t["topic"], 0),
        reverse=True,
    )
    for t in outline:
        t["visit_count"] = topic_counts.get(t["topic"], 0)
        t["last_params"] = last_params_by_topic.get(t["topic"], {})

    return {"status": "success", "user_id": user_id, "outline": outline}


# ====================================================================
# 6. NASA / 太空新聞 API（含備援機制）
# ====================================================================

_NEWS_FALLBACK = [
    {
        "title": "韋伯望遠鏡發現遙遠星系",
        "sub_title": "揭示了宇宙早期恆星形成的全新軌跡與歷史...",
        "image_url": "https://picsum.photos/id/1015/300/180",
        "url": "https://www.nasa.gov",
    }
]


@router.get("/daily-knowledge")
async def get_daily_knowledge():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.spaceflightnewsapi.net/v4/articles/?limit=5",
                headers=headers,
            )

            if resp.status_code != 200:
                raise Exception(f"新聞 API 請求失敗，狀態碼：{resp.status_code}")

            raw_data = resp.json().get("results", [])

            news_list = [
                {
                    "title": item.get("title", "無標題"),
                    "sub_title": (item.get("summary", "") or "")[:80] + "...",
                    "image_url": item.get("image_url") or "https://via.placeholder.com/300x180",
                    "url": item.get("url", "#"),
                }
                for item in raw_data
            ]

            return {"status": "success", "data": news_list}

    except Exception as e:
        print(f"⚠️ 抓取太空新聞失敗，觸發 Fallback: {e}")
        return {"status": "fallback", "data": _NEWS_FALLBACK}
