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

from app.infrastructure.external_ai.gemini_service import GeminiService
from app.infrastructure.external_ai.pinecone_service import PineconeService
from app.infrastructure.database.sqlite_repository import SQLiteRepository
from app.use_cases.rag_chat_use_case import RAGChatUseCase
from app.adapters.controllers import chat_controller

# 2. 依賴注入
ai_service = GeminiService(api_keys=os.getenv("GEMINI_API_KEY", ""))
vector_store = PineconeService(
    api_key=os.getenv("PINECONE_API_KEY", ""),
    index_name=os.getenv("PINECONE_INDEX_NAME", "astro-knowledge")
)
db_repo = SQLiteRepository(db_path=str(BASE_DIR / "astro_platform.db"))

rag_use_case = RAGChatUseCase(
    ai_service=ai_service,
    vector_store=vector_store,
    session_repo=db_repo
)

app = FastAPI(title="StarLearn API - Clean Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 路由設置：首頁自動導向
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/login.html")

# 👈 加上這段：將 /home 指向 index.html
@app.get("/home", include_in_schema=False)
async def home_redirect():
    return RedirectResponse(url="/index.html")

chat_controller.set_use_case(rag_use_case)
app.include_router(chat_controller.router, prefix="/api")

# 4. 前端靜態資源掛載
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    # 👈 解決 /lab、/evolution 404 的萬用路由（自動匹配 .html）
    @app.get("/{page_name}")
    async def render_html_page(page_name: str):
        target_file = FRONTEND_DIR / page_name
        if target_file.is_file():
            return FileResponse(target_file)
        
        # 若網址沒有 .html，自動補上 .html 尋找
        html_file = FRONTEND_DIR / f"{page_name}.html"
        if html_file.is_file():
            return FileResponse(html_file)
            
        raise HTTPException(status_code=404, detail="頁面不存在")

    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)