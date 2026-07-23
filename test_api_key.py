import httpx
BASE_URL = "http://127.0.0.1:8000"


def test_server_status():
    """測試 1：後端伺服器是否開著 (Health Check)"""
    print("=" * 50)
    print("測試 1：檢查後端伺服器連線狀態 (/)")
    print("=" * 50)
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=3.0)
        if response.status_code == 200:
            print("🎉 成功！後端伺服器正常運行中。")
            print(f"回應內容：{response.json()}\n")
            return True
        else:
            print(f"⚠️ 後端回應異常，狀態碼：{response.status_code}\n")
            return False
    except httpx.ConnectError:
        print("❌ 連線失敗！請確認後端 FastAPI 是否已啟動。")
        print("👉 啟動指令：uvicorn main:app --reload\n")
        return False
    except Exception as e:
        print(f"❌ 發生未知錯誤：{e}\n")
        return False


def test_daily_knowledge_api():
    """測試 2：驗證今日天文新聞 API 格式與數據內容"""
    print("=" * 50)
    print("測試 2：驗證今日新聞 API (/api/daily-knowledge)")
    print("=" * 50)
    try:
        url = f"{BASE_URL}/api/daily-knowledge"
        response = httpx.get(url, timeout=10.0)

        # 1. 檢查 HTTP 狀態碼
        if response.status_code != 200:
            print(f"❌ API 請求失敗，HTTP 狀態碼：{response.status_code}")
            return

        data = response.json()
        status = data.get("status")
        news_list = data.get("data", [])

        print(f"📡 API 回傳狀態：{status}")

        # 2. 檢查資料類型是否為列表 (陣列)
        if not isinstance(news_list, list):
            print(
                f"❌ 資料格式錯誤：預期 data 為 list (陣列)，實際收到 {type(news_list).__name__}"
            )
            return

        if len(news_list) == 0:
            print("⚠️ 警告：回傳的新聞列表是空的！")
            return

        print(f"🎉 成功取得 {len(news_list)} 則新聞！\n")

        # 3. 抽查第一則新聞，驗證 key 是否缺失 (確保前端 render 不會爆掉)
        first_news = news_list[0]
        required_keys = ["title", "sub_title", "image_url", "url"]
        missing_keys = [k for k in required_keys if k not in first_news]

        if missing_keys:
            print(f"⚠️ 警告：第一則新聞缺少以下欄位：{missing_keys}")
        else:
            print("🔍 第一則新聞結構驗證通過：")
            print(f" ├─ 標題: {first_news.get('title')}")
            print(f" ├─ 摘要: {first_news.get('sub_title')}")
            print(f" ├─ 圖片: {first_news.get('image_url')}")
            print(f" └─ 連結: {first_news.get('url')}")

    except Exception as e:
        print(f"❌ 測試失敗，原因：{e}")


if __name__ == "__main__":
    # 先測試連線，若伺服器沒開就直接中斷測試
    if test_server_status():
        test_daily_knowledge_api()
