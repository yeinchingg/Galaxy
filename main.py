import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from rag_engine import AstronomyRAGEngine
from star_engine import StarSimulator
import storage
import api_routes

load_dotenv()
storage.init_db()

app = FastAPI(
    title="AI 助理",
    description="提供前端呼叫的 RAG API 服務",
)

# ------------------------------------------------------------------
# 1. 掛載靜態檔案目錄，讓瀏覽器能夠讀取專案裡的 html、css、js、fonts
# ------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="."), name="static")

# 目前前端沒有用到 cookie / session 驗證，所以不需要 allow_credentials=True。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 2. 設定無副檔名的乾淨網址路由
# ------------------------------------------------------------------


@app.get("/")
def root_redirect():
    """造訪根目錄時，自動強制導向登入頁"""
    return RedirectResponse(url="/login")


@app.get("/login")
def login_page():
    return FileResponse("login.html")


@app.get("/home")
def home_page():
    return FileResponse("index.html")


@app.get("/profile")
def profile_page():
    return FileResponse("profile.html")


@app.get("/lab")
def lab_page():
    return FileResponse("lab.html")


@app.get("/evolution")
def evolution_page():
    return FileResponse("evolution.html")


@app.get("/wiki")
def wiki_page():
    return FileResponse("wiki.html")


@app.get("/hr")
def hr_page():
    return FileResponse("hr.html")


@app.get("/quiz")
def quiz_page():
    return FileResponse("quiz.html")


# ------------------------------------------------------------------
# 建立共用的依賴物件，注入 api_routes
# ------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "my-gemini-database")

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


@app.get("/api-status")
def api_status():
    return {"status": "online", "message": "天文 RAG API 正在運行中！"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
