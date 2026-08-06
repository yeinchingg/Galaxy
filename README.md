# STARLEARN 探索太空支數位學習平台 

本專案是一個結合 **Clean Architecture** 設計理念的天文科普與恆星物理互動學習平台。系統整合 **RAG 檢索增強生成**、**恆星物理演化模型**、**3D 視覺化實驗室**、**SSE (Server-Sent Events) 實時串流對話** 與 **個人化學習大綱動態推薦** 等核心功能。

---

## Clean Architecture 分層分工與檔案歸屬

為提升系統的可維護性、擴充性與模組解耦，專案劃分為四大層級 (Clean Architecture Levels)。以下為明確的模組職責歸屬與規劃：

```text
starlearn/
├── 1. 前端網頁層 (Presentation Layer / User Interface)
│   ├── index.html           # 首頁 / 系統入口
│   ├── lab.html             # 3D 恆星實驗室互動介面
│   ├── evolution.html       # 恆星演化歷程展示
│   ├── hr.html              # 赫羅圖 (H-R Diagram) 觀測站
│   ├── quiz.html            # 星海問答與測驗
│   ├── wiki.html            # 宇宙知識百科庫
│   ├── login.html           # 使用者登入與身份驗證頁面
│   ├── profile.html         # 個人學習歷程與檔案
│   ├── auth.js              # 前端路由保護與驗證邏輯
│   ├── auth_handler.js      # 登入/註冊/訪客機制處理器
│   ├── fetch_news.js        # 太空新聞動態擷取邏輯
│   └── theme.css            # 全站 UI 主題樣式表
│
├── 2. 後端 API 層 (Interface Adapters / Web Controller)
│   ├── main.py              # 應用程式入口：FastAPI 初始化、CORS、依賴注入 (DI)
│   └── api_routes.py        # 端點控制層：定義 /api/* 路由與 Pydantic Schema
│
├── 3. AI 與業務邏輯服務層 (Application & Domain Business Logic)
│   ├── rag_engine.py        # RAG 檢索增強生成、SSE 串流對話引擎
│   └── star_engine.py       # 恆星物理模型計算與演化演算法
│   └── 外部 AI 服務 (External AI Services)
│       ├── Gemini API       # LLM 生成回答與向量嵌入 (Embedding)
│       └── Pinecone DB      # 雲端向量資料庫 (Vector Index)
│
├── 4. 資料儲存與基礎設施層 (Infrastructure / Data Access Layer)
│   ├── storage.py           # 資料庫存取介面 (SQLite / PostgreSQL DAO)
│   ├── astro_platform.db    # 現行本地 SQLite 資料庫檔案
│   └── (未來規劃) Redis      # 快取快照與 Session 高效存取
│
└──  環境設定與工具 (Config & Tools)
    ├── .env                 # 機密密鑰與 API Key 儲存檔 (已列入 .gitignore 防護)
    ├── .gitignore           # Git 忽略檔案清單
    ├── requirements.txt     # Python 套件依賴需求檔
    └── test_api_key.py      # API 金鑰效能與運作測試腳本
