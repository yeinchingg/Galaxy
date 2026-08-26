# app/infrastructure/news_client.py
import time
import requests


class SpaceflightNewsClient:
    def __init__(self):
        self.api_url = "https://api.spaceflightnewsapi.net/v4/articles"
        self._cache = {"data": None, "ts": 0.0}
        self.cache_ttl = 600

    def fetch_latest_news(self, limit: int = 6) -> list[dict]:
        now = time.time()
        if self._cache["data"] and (now - self._cache["ts"]) < self.cache_ttl:
            return self._cache["data"][:limit]

        try:
            resp = requests.get(
                self.api_url,
                params={"limit": limit, "ordering": "-published_at"},
                timeout=5,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])

            items = [
                {
                    "title": item.get("title", ""),
                    "summary": (item.get("summary") or "")[:120],
                    "image_url": item.get("image_url"),
                    "url": item.get("url", "#"),
                    "published_at": item.get("published_at", ""),
                    "source": item.get("news_site", "Spaceflight News"),
                }
                for item in results
            ]
            self._cache["data"] = items
            self._cache["ts"] = now
            return items[:limit]
        except Exception as e:
            print(f"⚠️ 外部新聞 API 抓取失敗，啟動降級機制: {e}")
            if self._cache["data"]:
                return self._cache["data"][:limit]
            # 離線或抓不到時的預設保底新聞
            return [
                {
                    "title": "【系統公告】太空新聞資料庫同步中",
                    "summary": "目前太空新聞外部 API 正在進行例行維護，您可以先至 3D 實驗室或赫羅圖觀測站進行模擬操作。",
                    "image_url": None,
                    "url": "#",
                    "published_at": "Just now",
                    "source": "STARLEARN System",
                }
            ]
