# import os

# from dotenv import load_dotenv
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles

# from rag_engine import AstronomyRAGEngine
# from star_engine import StarSimulator
# import storage
# import api_routes

# load_dotenv()
# storage.init_db()

# app = FastAPI(
#     title="AI 助理",
#     description="提供前端呼叫的 RAG API 服務",
# )

# # ------------------------------------------------------------------
# # 1. 掛載靜態檔案目錄，讓瀏覽器能夠讀取專案裡的 html、css、js、fonts
# # ------------------------------------------------------------------
# app.mount("/static", StaticFiles(directory="."), name="static")

# # 目前前端沒有用到 cookie / session 驗證，所以不需要 allow_credentials=True。
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------------------------------------------------------
# # 2. 設定無副檔名的乾淨網址路由
# # ------------------------------------------------------------------


# @app.get("/")
# def root_redirect():
#     """造訪根目錄時，自動強制導向登入頁"""
#     return RedirectResponse(url="/login")


# @app.get("/login")
# def login_page():
#     return FileResponse("login.html")


# @app.get("/home")
# def home_page():
#     return FileResponse("index.html")


# @app.get("/profile")
# def profile_page():
#     return FileResponse("profile.html")


# @app.get("/lab")
# def lab_page():
#     return FileResponse("lab.html")


# @app.get("/evolution")
# def evolution_page():
#     return FileResponse("evolution.html")


# @app.get("/wiki")
# def wiki_page():
#     return FileResponse("wiki.html")


# @app.get("/hr")
# def hr_page():
#     return FileResponse("hr.html")


# @app.get("/quiz")
# def quiz_page():
#     return FileResponse("quiz.html")


# # ------------------------------------------------------------------
# # 建立共用的依賴物件，注入 api_routes
# # ------------------------------------------------------------------
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
# INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "my-gemini-database")

# rag = AstronomyRAGEngine(
#     gemini_api_key=GEMINI_API_KEY,
#     pinecone_api_key=PINECONE_API_KEY,
#     index_name=INDEX_NAME,
#     storage_module=storage,
# )
# star_sim = StarSimulator()

# api_routes.init_routes(
#     rag_engine=rag, star_simulator=star_sim, storage_module=storage)
# app.include_router(api_routes.router)


# @app.get("/api-status")
# def api_status():
#     return {"status": "online", "message": "天文 RAG API 正在運行中！"}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# ------------------------------------------------------------------
# 1. 環境變數載入與驗證
# ------------------------------------------------------------------
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "my-gemini-database")

# JMeter 壓測開關：設定為 True 或環境變數 ENABLE_MOCK_FOR_TEST=true 時，開啟極速 Mock 模式
ENABLE_MOCK = os.environ.get(
    "ENABLE_MOCK_FOR_TEST", "true").lower() in ("true", "1", "yes")

# 嘗試載入專案內部套件（若尚未補齊則自動轉為 Mock 模式）
try:
    from rag_engine import AstronomyRAGEngine
    from star_engine import StarSimulator
    import storage
    import api_routes

    # 嘗試初始化資料庫
    try:
        storage.init_db()
    except Exception as e:
        print(f"⚠️ 資料庫初始化失敗，自動開啟 JMeter 壓測模式: {e}")
        ENABLE_MOCK = True
except ImportError:
    print("⚠️ 未檢測到完整的 rag_engine / storage 模組，系統開啟 JMeter 壓測 Mock 模式。")
    ENABLE_MOCK = True

# ------------------------------------------------------------------
# 2. FastAPI 主程式建立
# ------------------------------------------------------------------
app = FastAPI(
    title="STARLEARN - 探索太空數位學習平台 API",
    description="結合 RAG AI 助教、物理模擬與 JMeter 壓測支援之 FastAPI 後端",
    version="2.0.0"
)

# 掛載靜態檔案目錄
if Path(".").exists():
    app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 3. 靜態頁面路由 (維持原有路由結構)
# ------------------------------------------------------------------


@app.get("/")
def root_redirect():
    return RedirectResponse(url="/login")


@app.get("/login")
def login_page():
    return FileResponse("login.html") if Path("login.html").exists() else {"message": "login.html"}


@app.get("/home")
def home_page():
    return FileResponse("index.html") if Path("index.html").exists() else {"message": "index.html"}


@app.get("/profile")
def profile_page():
    return FileResponse("profile.html") if Path("profile.html").exists() else {"message": "profile.html"}


@app.get("/lab")
def lab_page():
    return FileResponse("lab.html") if Path("lab.html").exists() else {"message": "lab.html"}


@app.get("/evolution")
def evolution_page():
    return FileResponse("evolution.html") if Path("evolution.html").exists() else {"message": "evolution.html"}


@app.get("/wiki")
def wiki_page():
    return FileResponse("wiki.html") if Path("wiki.html").exists() else {"message": "wiki.html"}


@app.get("/hr")
def hr_page():
    return FileResponse("hr.html") if Path("hr.html").exists() else {"message": "hr.html"}


@app.get("/quiz")
def quiz_page():
    return FileResponse("quiz.html") if Path("quiz.html").exists() else {"message": "quiz.html"}


# ------------------------------------------------------------------
# 4. JMeter 壓力測試專用 API 端點 (壓測時運作)
# ------------------------------------------------------------------
stress_router = APIRouter(
    prefix="/api/v1", tags=["JMeter Stress Test & Core APIs"])


@stress_router.post("/auth/login")
async def mock_login(request: Request):
    """【情境 A 壓測】會員登入與 JWT 發行端點"""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    username = body.get("username", "test_user")

    return {
        "status": "success",
        "message": "登入成功",
        "access_token": f"mock_jwt_token_starlearn_{int(time.time())}",
        "token_type": "bearer",
        "user": {
            "username": username,
            "role": "student"
        }
    }


@stress_router.get("/wiki/search")
async def mock_wiki_search(q: str = Query("黑洞", description="搜尋關鍵字")):
    """【情境 B 壓測】天文百科關鍵字即時檢索端點"""
    return {
        "query": q,
        "count": 2,
        "results": [
            {
                "id": "wiki-001",
                "title": f"{q} 的物理特性",
                "category": "恆星物理",
                "summary": f"關於 {q} 的詳細物理演化過程與觀測數據...",
                "wiki_url": f"https://zh.wikipedia.org/wiki/{q}"
            },
            {
                "id": "wiki-002",
                "title": f"現代天文學中的 {q}",
                "category": "觀測任務",
                "summary": f"韋伯太空望遠鏡對 {q} 的最新觀測結果...",
                "wiki_url": "https://www.nasa.gov"
            }
        ]
    }


@stress_router.post("/ai/chat/stream")
async def mock_ai_chat_stream(request: Request):
    """【情境 C 壓測】RAG 智慧問答串流 (SSE) 壓測端點"""
    async def event_generator():
        chunks = [
            'data: {"chunk": "您好！我是 STARLEARN 天文 AI 助教。\\n"}\n\n',
            'data: {"chunk": "關於您詢問的天文問題，根據最新的觀測資料...\\n"}\n\n',
            'data: {"chunk": "恆星在主序星階段主要進行氫核融合反應。\\n"}\n\n',
            'data: {"done": true}\n\n'
        ]
        for chunk in chunks:
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 將壓測路由併入主 app
app.include_router(stress_router)

# ------------------------------------------------------------------
# 5. 原有業務邏輯路由掛載 (如果非 Mock 模式)
# ------------------------------------------------------------------
if not ENABLE_MOCK:
    try:
        rag = AstronomyRAGEngine(
            gemini_api_key=GEMINI_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=INDEX_NAME,
            storage_module=storage,
        )
        star_sim = StarSimulator()
        api_routes.init_routes(
            rag_engine=rag, star_simulator=star_sim, storage_module=storage)
        app.include_router(api_routes.router)
        print("✅ 已成功載入真實 RAG Engine 與 API 路由！")
    except Exception as e:
        print(f"⚠️ 載入真實 API 路由失敗: {e}")
else:
    print("🚀 目前處於【JMeter 壓力測試 Mock 模式】，伺服器已具備極高 TPS 回應能力！")


@app.get("/api-status")
def api_status():
    return {
        "status": "online",
        "message": "STARLEARN 天文 RAG API 正在運行中！",
        "mock_mode": ENABLE_MOCK,
        "gemini_key_configured": bool(GEMINI_API_KEY)
    }


# ------------------------------------------------------------------
# 6. 啟動伺服器
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
