from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from typing import Optional
import httpx

# 匯入物理引擎與儲存模組
from star_engine import StarSimulator
import storage

router = APIRouter(prefix="/api")

rag_engine = None
star_sim = StarSimulator()


def init_routes(engine):
    global rag_engine
    rag_engine = engine


class ChatRequest(BaseModel):
    question: str
    user_id: Optional[str] = "demo_user"
    session_id: Optional[str] = None
    top_k: Optional[int] = 3


class EvolveRequest(BaseModel):
    user_id: Optional[str] = "demo_user"
    mass: float
    metallicity: float
    rotation: float
    age_gyr: float
    with_hint: Optional[bool] = True


@router.post("/chat/session")
async def create_session():
    session_id = storage.new_session_id()
    return {"status": "success", "session_id": session_id}


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest):
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG Engine 未初始化")

    session_id = payload.session_id or storage.new_session_id()

    # 保存使用者輸入訊息至 SQLite
    storage.save_message(session_id, "user", payload.question)

    async def event_generator():
        # 1. Pinecone 向量檢索
        retrieved = rag_engine.retrieve_context(
            payload.question, top_k=payload.top_k)

        full_response = ""

        # 2. 生成串流回答
        for chunk in rag_engine.generate_stream(payload.question, retrieved):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # 3. 保存 AI 回應訊息至 SQLite
        storage.save_message(session_id, "assistant", full_response)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/star/evolve")
async def evolve_star(payload: EvolveRequest):
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG Engine 未初始化")

    # 紀錄使用者調整參數的操作
    storage.log_interaction(
        user_id=payload.user_id,
        topic="star_lifecycle",
        action="adjust_params",
        params=payload.model_dump()
    )

    # 1. 使用 star_engine 進行嚴謹物理演化計算
    evolve_result = star_sim.evolve(
        mass=payload.mass,
        metallicity=payload.metallicity,
        rotation=payload.rotation,
        age_gyr=payload.age_gyr
    )

    # 2. 動態產生提示句 (Hint)
    hint_text = ""
    if payload.with_hint:
        desc = (
            f"質量:{evolve_result['mass']}M☉, "
            f"階段:{evolve_result['stage_name']}, "
            f"溫度:{evolve_result['current_temperature_k']}K"
        )
        hint_text = rag_engine.generate_short_hint(desc)

    return {
        "status": "success",
        "data": evolve_result,
        "hint": hint_text
    }


@router.get("/api/daily-knowledge")
async def get_daily_knowledge():
    try:
        # 加入 headers 模擬真實瀏覽器，並關閉 SSL 驗證避免本地端憑證問題
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(verify=False, timeout=8.0) as client:
            resp = await client.get(
                "https://api.spaceflightnewsapi.net/v4/articles/?limit=5",
                headers=headers
            )

            if resp.status_code != 200:
                print(f"❌ 新聞 API 回傳狀態碼異常: {resp.status_code}")
                raise Exception(f"新聞 API 請求失敗，狀態碼：{resp.status_code}")

            raw_data = resp.json().get("results", [])

            news_list = []
            for item in raw_data:
                news_list.append({
                    "title": item.get("title", "無標題"),
                    "sub_title": item.get("summary", "")[:80] + "...",
                    "image_url": item.get("image_url", "https://via.placeholder.com/300x180"),
                    "url": item.get("url", "#"),
                })

            return {"status": "success", "data": news_list}

    except Exception as e:
        # 在控制台印出真正的失敗原因，方便除錯
        print(f"⚠️ 抓取太空新聞失敗，觸發 Fallback: {e}")
        return {
            "status": "fallback",
            "data": [
                {
                    "title": "韋伯望遠鏡發現遙遠星系",
                    "sub_title": "揭示了宇宙早期恆星形成的全新軌跡與歷史...",
                    "image_url": "https://picsum.photos/id/1015/300/180",
                    "url": "https://www.nasa.gov",
                }
            ],
        }


@router.get("/outline/{user_id}")
async def get_user_outline(user_id: str):
    """使用者學習大綱 API (包含 visit_count)"""
    return {
        "status": "success",
        "user_id": user_id,
        "outline": [
            {"id": 1, "title": "恆星主序星階段", "visit_count": 3},
            {"id": 2, "title": "紅巨星與重力塌縮", "visit_count": 0}
        ]
    }


@router.post("/track")
async def track_user_action(payload: dict):
    """使用者行為追蹤 API"""
    user_id = payload.get("user_id", "demo_user")
    topic = payload.get("topic", "general")
    action = payload.get("action", "click")
    params = payload.get("params", {})

    storage.log_interaction(user_id, topic, action, params)
    return {"status": "success"}
