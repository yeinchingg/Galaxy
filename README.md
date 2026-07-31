# FastAPI API Routes 專案說明文件

本專案為一個結合 **RAG (檢索增強生成) 智慧問答**、**恆星物理演化模擬**、**3D 場景導覽** 及 **個人化學習大綱推薦** 的天文科普 API 服務平台。

系統採用 **FastAPI** 框架構建，採用依賴注入與模組化架構設計，將 API 路由、業務邏輯與資料存取層完整解耦。

---

## 目錄

- [專案架構](#專案架構)
- [環境需求與安裝](#環境需求與安裝)
- [快速啟動](#快速啟動)
- [架構設計說明](#架構設計說明)
- [API 功能說明與端點清單](#api-功能說明與端點清單)
  - [1. 智慧問答 (RAG)](#1-智慧問答-rag)
  - [2. 對話紀錄與串流 (Chat & History)](#2-對話紀錄與串流-chat--history)
  - [3. 恆星模擬器 (Star Simulator)](#3-恆星模擬器-star-simulator)
  - [4. 3D 場景導覽 (3D Narration)](#4-3d-場景導覽-3d-narration)
  - [5. 學習追蹤與動態大綱 (User Tracking & Outline)](#5-學習追蹤與動態大綱-user-tracking--outline)
  - [6. 每日知識與太空新聞 (Daily Knowledge)](#6-每日知識與太空新聞-daily-knowledge)
- [例外處理與備援機制](#例外處理與備援機制)

---

## 專案架構

```text
.
├── main.py              # 應用程式入口點：初始化 FastAPI、CORS、組件依賴注入
├── api_routes.py        # API 路由定義與 Pydantic 資料模型規範
├── rag_engine.py        # RAG 檢索增強生成與知識庫問答邏輯
├── star_sim.py          # 恆星演化計算引擎與參數模擬
├── storage.py           # 對話紀錄與使用者行為追蹤資料存取層
└── requirements.txt     # 專案套件依賴清單
```

---

## 環境需求與安裝

### 環境需求

- **Python**: 3.9 或以上版本
- **pip**: 最新版本包管理器

### 安裝步驟

1. **複製專案庫**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **建立並啟用虛擬環境 (建議)**

   ```bash
   python -m venv venv
   # Linux / macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

3. **安裝依賴套件**

   ```bash
   pip install -r requirements.txt
   ```

   *如無 `requirements.txt`，請手動安裝核心套件：*

   ```bash
   pip install fastapi uvicorn pydantic httpx
   ```

---

## 快速啟動

### 1. 啟動 API 伺服器

執行以下命令啟動 Uvicorn 開發伺服器：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 存取 API 互動式文件

伺服器啟動後，可透過瀏覽器存取自動生成的 Swagger 與 ReDoc 文件進行端點測試：

- **Swagger UI 介面**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc 介面**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 架構設計說明

- **職責分離 (SoC)**：
  - `main.py` 負責整體應用程式生命週期管理（包括跨域設定 CORS、引擎實例化與元件掛載）。
  - `api_routes.py` 專注於 API 路由宣告、請求與回應的 Pydantic 模型驗證，不直接綁定全域單例。
- **依賴注入模式 (Dependency Injection)**：
  透過 `init_routes(rag_engine, star_sim, storage)` 函式將具體的服務實例動態注入路由模組，避免組件間的強耦合與循環匯入 (Circular Import) 問題。

---

## API 功能說明與端點清單

所有端點預設皆以 `/api` 為前綴。

### 1. 智慧問答 (RAG)

提供基於知識庫的天文知識問答功能。

- **POST /api/ask**
  - **說明**：執行通用天文知識 RAG 檢索與問答。
  - **Request Body**：
    ```json
    {
      "question": "黑洞是如何形成的？",
      "top_k": 3,
      "session_id": "optional-session-id"
    }
    ```
- **POST /api/qa/topic**
  - **說明**：針對指定特定主題進行限定範圍的知識檢索問答。
  - **Request Body**：
    ```json
    {
      "question": "太陽未來的演化階段？",
      "topic": "star_evolution",
      "top_k": 3,
      "session_id": "optional-session-id"
    }
    ```

### 2. 對話紀錄與串流 (Chat & History)

支援 Session 對話管理以及 SSE 實時打字機效果回應。

- **POST /api/chat/session**
  - **說明**：建立新的對話階段並傳回 `session_id`。
- **GET /api/chat/history/{session_id}**
  - **說明**：根據 `session_id` 撈取該對話歷史記錄清單。
- **POST /api/chat/stream**
  - **說明**：以 Server-Sent Events (SSE) 格式實時串流輸出模型回答。系統會自動在串流啟動與結束時完成對話紀錄寫入。

### 3. 恆星模擬器 (Star Simulator)

計算不同初始參數下恆星的物理狀態與演化過程。

- **POST /api/star/initial**
  - **說明**：根據恆星質量、金屬量與自轉計算初始物理參數。
  - **Request Body**：
    ```json
    {
      "mass": 1.0,
      "metallicity": 1.0,
      "rotation": 0.0
    }
    ```
- **POST /api/star/evolve**
  - **說明**：模擬恆星隨時間演化的過程，支援傳回導覽提示句 (Hint) 並紀錄使用者操作。
  - **Request Body**：
    ```json
    {
      "mass": 1.0,
      "metallicity": 1.0,
      "rotation": 0.0,
      "age_gyr": 4.6,
      "with_hint": true,
      "user_id": "user-123"
    }
    ```

### 4. 3D 場景導覽 (3D Narration)

- **POST /api/3d/narrate**
  - **說明**：接收 3D WebGL 場景當前的情境描述，生成對應的語音導覽與解說字幕。
  - **Request Body**：
    ```json
    {
      "context_description": "玩家正在接近一顆超新星爆炸殘骸"
    }
    ```

### 5. 學習追蹤與動態大綱 (User Tracking & Outline)

- **POST /api/track**
  - **說明**：紀錄使用者在前端頁面的互動行為與操作參數。
- **GET /api/outline/{user_id}**
  - **說明**：分析指定使用者的歷程與偏好，動態產生個人化學習大綱與章節建議。

### 6. 每日知識與太空新聞 (Daily Knowledge)

- **GET /api/daily-knowledge**
  - **說明**：取得最新太空新聞與每日知識卡片。

---

## 例外處理與備援機制

- **第三方 API 容錯 (Fallback Mechanism)**：
  在 `/api/daily-knowledge` 串接外部 Spaceflight News API 時，設定有 **8 秒請求超時限制**。當外部服務異常或逾時時，系統會自動捕捉例外並改為回傳預設備援新聞資料，確保前端介面持續可用。
- **統一錯誤回應**：
  若傳入不合規定的參數， Fast API 將自動回傳 HTTP status `422 Unprocessable Entity` 並附帶明確欄位錯誤訊息。
