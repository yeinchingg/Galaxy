import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 目前前端沒有用到 cookie / session 驗證，所以不需要 allow_credentials=True。
# allow_origins=["*"] + allow_credentials=False 是合法且安全的組合，
# 不會像「* + credentials=True」那樣被瀏覽器擋，也不會像白名單那樣
# 因為 index.html / lab.html 開啟的 origin（file:// 或某個 dev server port）
# 沒被列到而被 CORS 中介層擋掉 OPTIONS 預檢。
#
# 如果之後真的需要帶 cookie/session（例如做登入功能），
# 再改回明確列出正式網域的白名單 + allow_credentials=True。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 建立共用的依賴物件，注入 api_routes，讓 main.py 只做「整體組裝」，
# 所有路由細節（Schema、商業邏輯）都集中在 api_routes.py。
# ------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "my-gemini-database")

rag = AstronomyRAGEngine(
    gemini_api_key=GEMINI_API_KEY,
    pinecone_api_key=PINECONE_API_KEY,
    index_name=INDEX_NAME,
    storage_module=storage,  # 讓 rag engine 可以讀對話歷史做「記憶」
)
star_sim = StarSimulator()

api_routes.init_routes(rag_engine=rag, star_simulator=star_sim, storage_module=storage)
app.include_router(api_routes.router)


@app.get("/")
def home():
    return {"status": "online", "message": "天文 RAG API 正在運行中！"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
