# STARLEARN 探索太空數位學習平台

本專案是一個結合 Clean Architecture 設計理念的天文科普與恆星物理互動學習平台。系統整合 RAG 檢索增強生成、恆星物理演化模型、3D 視覺化實驗室、SSE 實時串流對話與個人化學習大綱動態推薦等核心功能。

---

## 核心功能

- 3D 恆星實驗室：透過互動式 3D 視覺化，觀察恆星結構與物理特性
- 恆星演化模型：以物理演算法模擬恆星從誕生到死亡的完整生命週期
- RAG 智能問答：結合向量檢索與 LLM 生成，提供精準的天文知識問答
- SSE 實時串流對話：低延遲、逐字串流的對話體驗
- 赫羅圖 (H-R Diagram) 觀測站：視覺化呈現恆星光譜與亮度分類
- 星海問答與測驗：檢核學習成效的互動測驗模組
- 宇宙知識百科庫：系統化整理的天文知識庫
- 使用者驗證機制：完整的登入 / 註冊 / 訪客模式支援
- 太空新聞動態擷取：即時同步最新太空探索資訊

---

## 專案架構

專案採用 Clean Architecture 劃分為四大層級，模組職責歸屬如下：

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
└── 環境設定與工具 (Config & Tools)
    ├── .env                 # 機密密鑰與 API Key 儲存檔（已列入 .gitignore 防護）
    ├── .gitignore           # Git 忽略檔案清單
    ├── requirements.txt     # Python 套件依賴需求檔
    └── test_api_key.py      # API 金鑰效能與運作測試腳本
```

---

## 安裝

### 環境需求

- Python 3.10 或更高版本
- Git
- 資料庫：SQLite 3（現行）／ PostgreSQL 14+ ／ Redis（未來規劃）
- 支援 WebGL / HTML5 的現代瀏覽器（Chrome、Edge、Safari）
- 第三方 API 金鑰：
  - [Google Gemini API Key](https://aistudio.google.com/)（用於 RAG 問答與向量生成）
  - [Pinecone API Key](https://www.pinecone.io/)（用於向量資料庫檢索）

### 步驟

**1. 複製儲存庫**

```bash
git clone https://github.com/your-username/starlearn.git
cd starlearn
```

**2. 建立並啟用虛擬環境**

macOS / Linux：

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows（CMD / PowerShell）：

```bash
python -m venv venv
.\venv\Scripts\activate
```

**3. 安裝依賴套件**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

若前端有獨立的 Node/NPM 套件管理，請另外執行：

```bash
npm install
```

**4. 設定環境變數**

在專案根目錄下建立 `.env` 檔案，並填入 API 金鑰（可參考 `.env.example`）：

```
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1

PORT=8000
DEBUG=True
```

**5. 初始化資料庫**

```bash
python storage.py --init-db
```

---

## 快速啟動

```bash
python main.py
# 或使用 uvicorn 啟動
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

啟動成功後，開啟瀏覽器造訪：

- Web 介面首頁：http://127.0.0.1:8000/
- Swagger API 互動文件：http://127.0.0.1:8000/docs

---

## 環境變數

| 變數名稱 | 說明 | 必填 |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API 金鑰，用於生成回答與向量嵌入 | 是 |
| `PINECONE_API_KEY` | Pinecone 向量資料庫 API 金鑰 | 是 |
| `PINECONE_ENV` | Pinecone 服務所在的環境區域（例如 `us-east-1`） | 是 |
| `PORT` | 服務啟動的埠號（預設 `8000`） | 否 |
| `DEBUG` | 是否開啟除錯模式（`True` / `False`） | 否 |

`.env` 檔案已列入 `.gitignore`，請勿將金鑰提交至版本控制系統。

---

## API 文件

專案基於 FastAPI 建置，啟動服務後可於 `/docs` 取得自動生成的 Swagger UI 文件，涵蓋：

- `/api/chat`：RAG 問答與 SSE 串流對話端點
- `/api/star`：恆星物理演化模型計算端點
- `/api/auth`：使用者登入 / 註冊 / 身份驗證端點

詳細的請求與回應 Schema 請參考 `api_routes.py` 中的 Pydantic 模型定義。

---

 ## Roadmap

- 導入 PostgreSQL 取代現行 SQLite，支援更高併發存取
- 整合 Redis 作為快取層，加速 Session 與熱門查詢
- 擴充個人化學習大綱動態推薦演算法
- 新增多語系（i18n）支援
- 補充完整的單元測試與 CI/CD 流程

---
## 透過 Issue 或 Pull Request 參與開發

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

