from locust import HttpUser, task, between
import random

class StarLearnLoadTestUser(HttpUser):
    # 模擬使用者在每次操作間停頓 1 到 3 秒
    wait_time = between(1, 3)

    def on_start(self):
        """每個虛擬使用者啟動時建立一個獨立訪客身份"""
        res = self.client.post("/api/auth/guest", json={"display_name": f"壓測訪客_{random.randint(1000, 9999)}"})
        if res.status_code == 200:
            self.user_id = res.json().get("user_id", 1)
        else:
            self.user_id = 1

    @task(4)
    def test_daily_knowledge_load(self):
        """首頁新聞與備援池高頻存取"""
        self.client.get("/api/daily-knowledge")

    @task(3)
    def test_sky_observe_ingestion(self):
        """觀測軌跡寫入測試"""
        targets = ["太陽", "木星", "火星 (Mars)", "仙女座大星系 (M31)", "天狼星"]
        self.client.post("/api/sky/observe", json={
            "name": random.choice(targets),
            "body_type": "恆星",
            "alt": random.uniform(10.0, 80.0),
            "az": random.uniform(0.0, 360.0),
            "mag": random.uniform(-1.5, 6.0),
            "user_id": str(self.user_id)
        })

    @task(2)
    def test_ai_3d_narration(self):
        """3D 實驗室 AI 動態旁白分析"""
        self.client.post("/api/3d/narrate", json={
            "context_description": f"質量 {random.uniform(0.5, 5.0)} M☉, 暗物質密度 {random.uniform(0.1, 0.9)} pc"
        })

    @task(1)
    def test_chat_stream_load(self):
        """AI 對話串流長連線測試"""
        with self.client.post("/api/chat/stream", json={
            "question": "恆星如何演化為超新星？",
            "user_id": self.user_id
        }, stream=True, catch_response=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if b"done" in line:
                        break
                response.success()
            else:
                response.failure(f"串流失敗狀態碼: {response.status_code}")