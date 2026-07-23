import os
import collections
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from rag_engine import AstronomyRAGEngine
from star_engine import StarSimulator
import storage
import httpx

load_dotenv()
storage.init_db()

app = FastAPI(
    title="AI 助理",
    description="提供前端呼叫的 RAG API 服務"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "my-gemini-database")

rag = AstronomyRAGEngine(
    gemini_api_key=GEMINI_API_KEY,
    pinecone_api_key=PINECONE_API_KEY,
    index_name=INDEX_NAME
)
star_sim = StarSimulator()  # 修正：名稱對齊下方呼叫


@app.get("/")
def home():
    return {"status": "online", "message": "天文 RAG API 正在運行中！"}


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


@app.post("/api/ask")
def ask_astronomy(payload: QuestionRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    result = rag.ask(payload.question, top_k=payload.top_k)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result

# =====================================================================
# 1. 使用者互動紀錄 + 動態課程大綱
# =====================================================================


class TrackRequest(BaseModel):
    user_id: str
    topic: str
    action: str
    params: dict = {}


@app.post("/api/track")
def track_interaction(payload: TrackRequest):
    storage.log_interaction(payload.user_id, payload.topic,
                            payload.action, payload.params)
    return {"status": "success"}


@app.get("/api/outline/{user_id}")
def get_outline(user_id: str):
    interactions = storage.get_recent_interactions(user_id, limit=100)
    topic_counts = collections.Counter(i["topic"] for i in interactions)
    last_params_by_topic: dict[str, dict] = {}
    for i in interactions:
        if i["topic"] not in last_params_by_topic and i["params"]:
            last_params_by_topic[i["topic"]] = i["params"]

    all_topics = [
        {"topic": "physics_meaning", "title": "物理數據的意義"},
        {"topic": "star_lifecycle", "title": "恆星的一生"},
        {"topic": "chat", "title": "對話空間"},
        {"topic": "3d", "title": "3D 投影"},
    ]

    outline = sorted(
        all_topics,
        key=lambda t: topic_counts.get(t["topic"], 0),
        reverse=True,
    )
    for t in outline:
        t["visit_count"] = topic_counts.get(t["topic"], 0)
        t["last_params"] = last_params_by_topic.get(t["topic"], {})

    return {"status": "success", "user_id": user_id, "outline": outline}

# =====================================================================
# 2. 恆星模擬 API
# =====================================================================


class StarInitialRequest(BaseModel):
    mass: float
    metallicity: float = 1.0
    rotation: float = 0.0


class StarEvolveRequest(StarInitialRequest):
    age_gyr: float
    with_hint: bool = False


@app.post("/api/star/initial")
def star_initial(payload: StarInitialRequest):
    return {"status": "success", "data": star_sim.compute_initial(
        payload.mass, payload.metallicity, payload.rotation)}


@app.post("/api/star/evolve")
def star_evolve(payload: StarEvolveRequest):
    result = star_sim.evolve(
        payload.mass, payload.metallicity, payload.rotation, payload.age_gyr)
    response = {"status": "success", "data": result}

    if payload.with_hint:
        description = f"質量{payload.mass}倍太陽、目前階段：{result['stage_name']}、溫度約{result['current_temperature_k']}K"
        response["hint"] = rag.generate_short_hint(description)

    return response

# =====================================================================
# 3. 智慧問答
# =====================================================================


class TopicQuestionRequest(BaseModel):
    question: str
    topic: str = "chat"
    top_k: int = 3


@app.post("/api/qa/topic")
def ask_topic(payload: TopicQuestionRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    result = rag.ask_topic(
        payload.question, payload.topic, top_k=payload.top_k)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

# =====================================================================
# 4. 對話紀錄
# =====================================================================


@app.post("/api/chat/session")
def create_session():
    return {"status": "success", "session_id": storage.new_session_id()}


@app.get("/api/chat/history/{session_id}")
def get_chat_history(session_id: str):
    return {"status": "success", "session_id": session_id, "messages": storage.get_history(session_id)}

# =====================================================================
# 5. 串流回應
# =====================================================================


class StreamChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    top_k: int = 3


@app.post("/api/chat/stream")
def chat_stream(payload: StreamChatRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="問題內容不能為空")

    session_id = payload.session_id or storage.new_session_id()
    storage.save_message(session_id, "user", payload.question)

    def event_generator():
        retrieved = rag.retrieve_context(payload.question, top_k=payload.top_k)
        full_answer = []
        yield f"event: session\ndata: {session_id}\n\n"
        for chunk in rag.generate_stream(payload.question, retrieved):
            full_answer.append(chunk)
            yield f"data: {chunk}\n\n"
        storage.save_message(session_id, "assistant", "".join(full_answer))
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class NarrateRequest(BaseModel):
    context_description: str


@app.post("/api/3d/narrate")
def narrate_3d(payload: NarrateRequest):
    hint = rag.generate_short_hint(payload.context_description)
    return {"status": "success", "hint": hint}

# =====================================================================
# 6. NASA / 太空新聞 API
# =====================================================================


@app.get("/api/daily-knowledge")
async def get_daily_knowledge():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.spaceflightnewsapi.net/v4/articles/?limit=5",
                timeout=5.0,
            )
            if resp.status_code != 200:
                raise Exception("新聞 API 請求失敗")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
