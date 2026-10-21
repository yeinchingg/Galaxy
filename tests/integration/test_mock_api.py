"""Mock 測試（API 層）：SL-TC-HM-04 新聞備援、SL-TC-LB-16 串流仍送出 done。
放在 tests/integration/。只掛載 chat_controller 的 router，不會啟動 Gemini/Pinecone。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
pytest.importorskip("fastapi")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.adapters.controllers import chat_controller

app = FastAPI()
app.include_router(chat_controller.router, prefix="/api")
client = TestClient(app)


class FakeResp:
    def __init__(self, status, results=None):
        self.status_code, self._r = status, results or []
    def json(self):
        return {"results": self._r}


# ---------------- SL-TC-HM-04 ----------------
def test_hm_04_news_500_uses_fallback(monkeypatch):
    monkeypatch.setattr(chat_controller.requests, "get", lambda *a, **k: FakeResp(500))
    data = client.get("/api/news").json()
    assert data == chat_controller.NEWS_FALLBACK_POOL

def test_hm_04_news_timeout_uses_fallback(monkeypatch):
    def boom(*a, **k):
        raise TimeoutError("timeout")
    monkeypatch.setattr(chat_controller.requests, "get", boom)
    assert client.get("/api/news").json() == chat_controller.NEWS_FALLBACK_POOL

def test_hm_04_news_only_one_item_uses_fallback(monkeypatch):
    one = [{"title": "t", "summary": "s", "image_url": "u", "url": "x"}]
    monkeypatch.setattr(chat_controller.requests, "get", lambda *a, **k: FakeResp(200, one))
    assert client.get("/api/news").json() == chat_controller.NEWS_FALLBACK_POOL

def test_hm_04_daily_knowledge_shape(monkeypatch):
    monkeypatch.setattr(chat_controller.requests, "get", lambda *a, **k: FakeResp(500))
    body = client.get("/api/daily-knowledge").json()
    assert body["status"] == "success" and len(body["data"]) >= 1

def test_hm_01_summary_not_over_110_chars(monkeypatch):
    long = [{"title": "t", "summary": "字" * 300, "image_url": "u", "url": "x"}] * 3
    monkeypatch.setattr(chat_controller.requests, "get", lambda *a, **k: FakeResp(200, long))
    sub = client.get("/api/news").json()[0]["sub_title"]
    # 現況：110 字 + "..." = 113 字，與測試文件「不超過 110 字」不符
    assert len(sub) <= 110


# ---------------- SL-TC-LB-16 ----------------
class FakeUseCaseAllFail:
    def generate_stream(self, q, top_k=3, session_id=None):
        yield "[錯誤] 所有模型與 API Key 組合皆無法完成串流回應: x"

def test_lb_16_stream_error_still_sends_done(monkeypatch):
    monkeypatch.setattr(chat_controller, "_use_case", FakeUseCaseAllFail())
    monkeypatch.setattr(chat_controller, "_db_repo", None)
    text = client.post("/api/chat/stream", json={"question": "hi"}).text
    assert "[錯誤]" in text and "event: done" in text and "event: session" in text

def test_lb_16_stream_exception_still_sends_done(monkeypatch):
    class Boom:
        def generate_stream(self, *a, **k):
            raise RuntimeError("boom")
    monkeypatch.setattr(chat_controller, "_use_case", Boom())
    monkeypatch.setattr(chat_controller, "_db_repo", None)
    text = client.post("/api/chat/stream", json={"question": "hi"}).text
    assert "event: done" in text


# ---------------- 發現的缺陷：SSE 多行內容 ----------------
@pytest.mark.xfail(reason="chunk 內含換行時，SSE 的 data: 行會被切斷，前端只讀 data: 開頭的行而遺失後面文字")
def test_stream_multiline_chunk_is_valid_sse(monkeypatch):
    class Multi:
        def generate_stream(self, *a, **k):
            yield "重點：\n- 事件視界\n- 奇異點"
    monkeypatch.setattr(chat_controller, "_use_case", Multi())
    monkeypatch.setattr(chat_controller, "_db_repo", None)
    text = client.post("/api/chat/stream", json={"question": "hi"}).text
    for line in text.splitlines():
        assert line == "" or line.startswith(("data:", "event:"))
