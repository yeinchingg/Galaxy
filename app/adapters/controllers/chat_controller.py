"""
app/adapters/controllers/chat_controller.py
負責處理聊天對話、SSE 串流、3D 動態旁白、NASA 獨立專屬新聞連結、大綱推薦與行為追蹤 API
"""

import os
import uuid
import random
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.use_cases.rag_chat_use_case import RAGChatUseCase

router = APIRouter()
_use_case: Optional[RAGChatUseCase] = None


def set_use_case(use_case: RAGChatUseCase):
    global _use_case
    _use_case = use_case


# ---------------- Schema 定義 ----------------
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 3


class NarrateRequest(BaseModel):
    context_description: str


class TrackRequest(BaseModel):
    user_id: str
    topic: str
    action: str
    params: Dict[str, Any] = {}


# 👈 每一則新聞均配置專屬且各自獨立的 NASA 深度報導連結
NASA_FALLBACK_POOL = [
    {
        "title": "NASA's Webb Discovers Ancient Galaxy Clusters",
        "sub_title": "JWST deep field observations unveil massive clusters formed just hundreds of millions of years after the Big Bang.",
        "image_url": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/missions/webb/nasas-webb-reveals-intricate-details-in-early-universe-galaxies/"
    },
    {
        "title": "Hubble Views a Sparkling Spiral Galaxy in Deep Space",
        "sub_title": "The NASA/ESA Hubble Space Telescope captures intricate spiral arms glowing with newly born blue stars.",
        "image_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/missions/hubble/hubble-views-a-glittering-spiral-galaxy/"
    },
    {
        "title": "Artemis Program: NASA's Path to Lunar Exploration",
        "sub_title": "Space Launch System and Orion spacecraft prepare for human exploration of the lunar South Pole.",
        "image_url": "https://images.unsplash.com/photo-1517976487502-d7e35b7194f1?w=500&auto=format&fit=crop&q=80",
        "url": "https://www.nasa.gov/humans-in-space/artemis/"
    },
    {
        "title": "Perseverance Rover Explores River Delta on Mars",
        "sub_title": "NASA's rover samples sedimentary rocks in Jezero Crater to search for signs of ancient microscopic life.",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/mission/mars-2020-perseverance/"
    },
    {
        "title": "Chandra Probes Supermassive Black Hole Relativistic Jets",
        "sub_title": "High-energy X-ray emissions reveal powerful matter beams ejecting from galactic centers.",
        "image_url": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/missions/chandra/nasas-chandra-catches-supermassive-black-hole-in-action/"
    },
    {
        "title": "NASA's Europa Clipper Mission to Ocean World",
        "sub_title": "Investigating Jupiter's icy moon Europa to determine if conditions suitable for life exist beneath its crust.",
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/mission/europa-clipper/"
    },
    {
        "title": "Parker Solar Probe Touches the Sun's Corona",
        "sub_title": "Flying through the extreme environment of the solar atmosphere to unravel solar wind mysteries.",
        "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/mission/parker-solar-probe/"
    },
    {
        "title": "Juno Spacecraft Captures Volcanic Plumes on Io",
        "sub_title": "Close flybys of Jupiter's moon Io reveal dynamic lava lakes and dynamic planetary volcanism.",
        "image_url": "https://images.unsplash.com/photo-1545156521-77bd85671d30?w=500&auto=format&fit=crop&q=80",
        "url": "https://science.nasa.gov/mission/juno/"
    }
]


# ---------------- API 端點 ----------------

@router.get("/status")
def get_system_status():
    """提供連線與 AI 模組狀態"""
    return {
        "status": "online",
        "service": "StarLearn Astro Platform",
        "ai_ready": _use_case is not None
    }


@router.get("/daily-knowledge")
def get_daily_knowledge():
    """每日隨機自 NASA 抽取新聞，並生成專屬獨立網址"""
    nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    news_items = []

    # 1. 向 NASA 官方 APOD API 隨機抽取 4 則
    try:
        url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}&count=4"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            for item in data:
                if item.get("media_type") == "image":
                    date_str = item.get("date", "")
                    # 👈 轉換日期為 NASA 專屬獨立永久頁面格式 (如 2023-11-04 -> ap231104.html)
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        apod_specific_url = f"https://apod.nasa.gov/apod/ap{dt.strftime('%y%m%d')}.html"
                    except Exception:
                        apod_specific_url = "https://apod.nasa.gov/apod/archivepix.html"

                    news_items.append({
                        "title": item.get("title", "NASA Astronomy Picture of the Day"),
                        "sub_title": (item.get("explanation", "")[:120] + "..."),
                        "image_url": item.get("url") or item.get("hdurl"),
                        "url": apod_specific_url  # 專屬獨立新聞網址
                    })
    except Exception as e:
        print(f"⚠️ NASA APOD 請求逾時 ({e})，使用隨機精選庫...")

    # 2. 若 API 資料不足，從具備各篇專屬連結的精選池隨機補充
    if len(news_items) < 4:
        needed = 5 - len(news_items)
        sampled = random.sample(NASA_FALLBACK_POOL, min(len(NASA_FALLBACK_POOL), needed))
        news_items.extend(sampled)

    # 3. 隨機打亂排序
    random.shuffle(news_items)

    return {
        "status": "success",
        "data": news_items
    }


@router.get("/outline/{user_id}")
def get_outline(user_id: str):
    """個人化大綱推薦"""
    return {
        "status": "success",
        "user_id": user_id,
        "outline": [
            {"topic": "stellar_evolution", "title": "恆星演化史與赫羅圖", "visit_count": 3},
            {"topic": "black_hole", "title": "黑洞物理與重力透鏡", "visit_count": 1}
        ]
    }


@router.post("/track")
def track_user_action(req: TrackRequest):
    """使用者行為追蹤"""
    return {"status": "tracked"}


@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    """一般非串流對話"""
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")
    return _use_case.ask(req.question, top_k=req.top_k or 3, session_id=req.session_id)


@router.post("/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    """SSE 串流對話"""
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")

    session_id = req.session_id or f"session_{uuid.uuid4().hex[:8]}"

    def sse_event_generator():
        yield f"event: session\ndata: {session_id}\n\n"
        try:
            stream_gen = _use_case.generate_stream(
                req.question, 
                top_k=req.top_k or 3, 
                session_id=session_id
            )
            for chunk in stream_gen:
                if chunk:
                    yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: (AI 助理遇到暫時性問題: {str(e)})\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/3d/narrate")
def narrate_endpoint(req: NarrateRequest):
    """3D 實驗室動態旁白"""
    if not _use_case:
        raise HTTPException(status_code=500, detail="AI UseCase 尚未就緒")
    hint = _use_case.generate_short_hint(req.context_description)
    return {"hint": hint}