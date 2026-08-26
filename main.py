"""
main.py - StarLearn Clean Architecture 啟動入口
"""

from app.adapters.controllers import chat_controller
from app.use_cases.rag_chat_use_case import RAGChatUseCase
from app.infrastructure.database.database import SQLiteRepository
from app.infrastructure.external_ai.pinecone_service import PineconeService
from app.infrastructure.external_ai.gemini_service import GeminiService
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# 1. 載入環境變數
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# 2. 依賴注入 (DI Container 概念)
ai_service = GeminiService(api_keys=os.getenv("GEMINI_API_KEY", ""))
vector_store = PineconeService(
    api_key=os.getenv("PINECONE_API_KEY", ""),
    index_name=os.getenv("PINECONE_INDEX_NAME", "astro-knowledge"),
)

# 👈 完整嫁接 SQLite 資料庫儲存庫
db_path_str = str(BASE_DIR / "astro_platform.db")
db_repo = SQLiteRepository(db_path=db_path_str)

rag_use_case = RAGChatUseCase(
    ai_service=ai_service, vector_store=vector_store, session_repo=db_repo
)

app = FastAPI(title="StarLearn API - Clean Architecture Edition", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 路由設置：首頁與導向


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/login.html")


@app.get("/home", include_in_schema=False)
async def home_redirect():
    return RedirectResponse(url="/index.html")


# 注入 Use Case 給 Controller
chat_controller.set_use_case(rag_use_case)
app.include_router(chat_controller.router, prefix="/api")

# 4. 前端靜態資源與 HTML 萬用路由掛載
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/{page_name}")
    async def render_html_page(page_name: str):
        target_file = FRONTEND_DIR / page_name
        if target_file.is_file():
            return FileResponse(target_file)

        html_file = FRONTEND_DIR / f"{page_name}.html"
        if html_file.is_file():
            return FileResponse(html_file)

        raise HTTPException(status_code=404, detail="頁面不存在")

    app.mount(
        "/", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="frontend"
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
