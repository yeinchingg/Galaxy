
# 🌌 StarLearn - 天文物理多模態智慧學習平台

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Google Gemini API](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-000000?style=flat-square)](https://www.pinecone.io/)
[![Three.js](https://img.shields.io/badge/Frontend-Three.js_/_WebGL-black?style=flat-square&logo=three.js)](https://threejs.org/)
[![NASA Open API](https://img.shields.io/badge/Data-NASA_APOD_API-E03C31?style=flat-square&logo=nasa)](https://api.nasa.gov/)

> **StarLearn** 是一個結合 **RAG 檢索增強生成**、**3D 天體互動模擬**、**NASA 每日隨機天文探索** 與 **個人化學習路徑推薦** 的天文物理教育平台。

---

## 📑 目錄

- [專案簡介](#-專案簡介)
- [核心功能亮點](#-核心功能亮點)
- [系統架構與設計模式](#-系統架構與設計模式)
- [專案目錄結構](#-專案目錄結構)
- [技術棧](#-技術棧)
- [環境安裝與啟動教學](#-環境安裝與啟動教學)
- [後端 API 端點規格](#-後端-api-端點規格)


---

## 📖 專案簡介

本專案旨在解決傳統天文物理學習門檻高、抽象難懂的問題。透過以下核心技術實現沉浸式學習：
1. **檢索增強生成 (RAG)**：整合 Pinecone 向量資料庫與 Gemini 多金鑰容錯機制，精準回答專業天體物理問題。
2. **3D 即時動態實驗室**：使用 Three.js 模擬黑洞吸積盤、重力透鏡與恆星結構，並由 AI 根據畫面即時生成解說旁白。
3. **NASA 即時新知**：每日隨機串接 NASA 官方 APOD 資料庫與深度研究連結，提供即時的天文動態。
4. **個人化大綱與行為追蹤**：記錄使用者瀏覽足跡，自動推薦專屬延伸學習主題。

---

## ✨ 核心功能亮點

- 🤖 **AI 智慧導師 (SSE 串流對話)**：支援 Markdown 與 LaTeX 數學公式即時串流輸出，具備多對話輪次記憶。
- 🔑 **Gemini 多金鑰輪替機制 (Multi-Key Failover)**：自動偵測配額耗盡（429）或無效金鑰，秒級切換可用 Key，保證高可用性。
- 🔭 **3D 天體實驗室 (Interactive Lab)**：支援視角切換、物理參數調節與 AI 動態旁白生成。
- 🌠 **NASA 每日隨機新知輪播**：即時或隨機抽取 NASA 天文照片與摘要，點擊直達官方專屬報導頁面。
- 📊 **赫羅圖與恆星演化探索 (H-R Diagram)**：動態展示主序星、巨星、白矮星與超新星的演化路徑。
- 🎯 **個人化學習路徑**：基於前端行為追蹤演算法，即時計算學習興趣並推薦最佳探索大綱。

---

## 🏗 系統架構與設計模式

本專案後端嚴格遵循 **Clean Architecture（整潔架構）** 原則，實現高度模組化、低耦合與易於測試的特性：

```text
┌────────────────────────────────────────────────────────┐
│                   Frontend Client                      │
│   (index.html / lab.html / hr.html / wiki.html / JS)   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / SSE Stream
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Entrypoint (main.py)               │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│      Adapters / Controllers (chat_controller.py)       │
│  - REST API 路由 (/api/daily-knowledge, /api/outline)  │
│  - SSE 串流協議轉發 (/api/chat/stream)                  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│         Use Cases (rag_chat_use_case.py)               │
│  - RAG 檢索邏輯流程編排                                 │
│  - 對話歷史記錄管理                                     │
│  - 3D 場景語境旁白生成                                  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│      Infrastructure & External Services                │
│  ├── Gemini LLM (Multi-Key Rotation / Embedding)       │
│  ├── Pinecone Vector DB (天文知識庫語意搜尋)            │
│  └── NASA Open API (APOD 即時/隨機天文照片與報導)        │
└────────────────────────────────────────────────────────┘

```

---

## 📁 專案目錄結構

```text
website/
├── app/
│   ├── adapters/
│   │   └── controllers/
│   │       ├── __init__.py
│   │       └── chat_controller.py       # FastAPI 控制器與所有端點定義
│   ├── domain/                          # 核心業務實體與介面
│   ├── infrastructure/                  # 外部服務實作 (Gemini, Pinecone, NASA)
│   └── use_cases/
│       └── rag_chat_use_case.py         # RAG 檢索與對話用例
├── frontend/                            # 前端靜態資源
│   ├── css/                             # 樣式表 (深色太空風格)
│   ├── js/
│   │   ├── chat.js                      # AI 助理對話與 SSE 串流接收
│   │   ├── fetch_news.js                # 新聞隨機輪播、追蹤與大綱推薦
│   │   └── lab_3d.js                    # Three.js 3D 模擬與互動邏輯
│   ├── index.html                       # 平台首頁
│   ├── lab.html                         # 3D 天體互動實驗室
│   ├── hr.html                          # 赫羅圖與恆星演化
│   └── wiki.html                        # 天文知識庫百科
├── main.py                              # FastAPI 服務啟動入口
├── README.md                            # 專案說明文件
└── requirements.txt                     # Python 相依套件清單

```

---

## 🛠 技術棧

### 後端 (Backend)

* **核心框架**：Python 3.11+、FastAPI、Uvicorn
* **AI / LLM**：Google Generative AI (Gemini 2.5 Flash / Pro)
* **向量檢索**：Pinecone Serverless Vector Database
* **外部資料**：NASA APOD API、Requests

### 前端 (Frontend)

* **視圖層**：HTML5、CSS3 (Glassmorphism 毛玻璃視覺設計)
* **3D 渲染引擎**：Three.js、WebGL
* **非同步與串流**：Fetch API、Server-Sent Events (SSE)
* **排版與解析**：Marked.js (Markdown 解析)、KaTeX (LaTeX 公式渲染)

---

## 🚀 環境安裝與啟動教學

### 1. 複製專案庫

```bash
git clone [https://github.com/your-username/StarLearn.git](https://github.com/your-username/StarLearn.git)
cd StarLearn

```

### 2. 建立並啟動 Python 虛擬環境

```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. 安裝相依套件

```bash
pip install -r requirements.txt

```

> 若無 `requirements.txt`，可直接安裝關鍵套件：
> ```bash
> pip install fastapi uvicorn google-generativeai pinecone-client python-dotenv requests pydantic
> 
> ```
> 
> 

---



## 🌐 後端 API 端點規格

| 方法 | 端點 | 說明 |
| --- | --- | --- |
| `GET` | `/api/status` | 檢查伺服器與 AI 引擎連線狀態 |
| `GET` | `/api/daily-knowledge` | 隨機獲取 NASA APOD 每日天文新知與專屬報導連結 |
| `GET` | `/api/outline/{user_id}` | 根據使用者 ID 取得推薦學習大綱 |
| `POST` | `/api/track` | 記錄使用者瀏覽行為與主題互動次數 |
| `POST` | `/api/chat` | 單次問答對話 (JSON 回應) |
| `POST` | `/api/chat/stream` | **SSE 串流問答**（打字機效果，支援對話輪次記憶） |
| `POST` | `/api/3d/narrate` | 傳入 3D 場景參數，由 AI 即時生成解說旁白 |

---

## 🖥 執行與預覽

啟動 FastAPI 伺服器：

```powershell
python main.py

```

啟動後打開瀏覽器訪問各個模組：

* 🌟 **首頁門戶**：`http://127.0.0.1:8000/index.html`
* 🌌 **3D 互動實驗室**：`http://127.0.0.1:8000/lab.html`
* 📊 **赫羅圖模擬**：`http://127.0.0.1:8000/hr.html`
* 📖 **天文百科知識庫**：`http://127.0.0.1:8000/wiki.html`
* 📑 **互動式 API 文件**：`http://127.0.0.1:8000/docs`

---

