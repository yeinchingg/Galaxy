"""
tests/unit/test_gemini_service_perf.py
效能相關單元測試：驗證「client 快取」與「timeout 設定」兩項優化確實生效。

這些測試不會打真正的 Gemini API，而是把 google.genai.Client 換成假物件，
確保：
1. Client 只在 GeminiService 初始化時建立一次（每組 key 一個），
   之後每次呼叫都是重複使用同一個物件，不會重新建立。
2. 每個 Client 建立時都有帶上 http_options.timeout，
   避免某次 API 呼叫卡住時無限期等待。
"""

import time
from unittest.mock import MagicMock

import pytest

from app.infrastructure.external_ai import gemini_service as gs_module
from app.infrastructure.external_ai.gemini_service import (
    GeminiService,
    REQUEST_TIMEOUT_MS,
)


@pytest.fixture
def fake_genai_client(monkeypatch):
    """把 genai.Client 換成計數用的假物件，紀錄每次呼叫的參數與次數。"""
    created_clients = []

    def fake_client_factory(**kwargs):
        client = MagicMock(name=f"FakeClient-{len(created_clients)}")
        client.init_kwargs = kwargs
        created_clients.append(client)
        return client

    monkeypatch.setattr(gs_module.genai, "Client", fake_client_factory)
    return created_clients


def test_client_created_once_per_key_not_per_call(fake_genai_client):
    """優化 3：Client 應該在 __init__ 時，依 key 數量各建立一次就好。"""
    service = GeminiService(api_keys=["key-a", "key-b", "key-c"])

    # 初始化完成後，應該剛好建立 3 個 client（每組 key 一個）
    assert len(fake_genai_client) == 3

    # 之後不管呼叫幾次 _get_next_client，都不應該再新建 client
    seen_ids = []
    for _ in range(10):
        client = service._get_next_client()
        seen_ids.append(id(client))

    assert len(fake_genai_client) == 3, "呼叫 _get_next_client 不應該產生新的 Client"

    # 應該是在既有的 3 個 client 之間輪流使用（round-robin）
    assert set(seen_ids) == {id(c) for c in fake_genai_client}


def test_timeout_configured_on_every_client(fake_genai_client):
    """優化 1：每個 Client 建立時都要帶上逾時設定，且值等於 REQUEST_TIMEOUT_MS。"""
    GeminiService(api_keys=["key-a", "key-b"])

    assert len(fake_genai_client) == 2
    for client in fake_genai_client:
        http_options = client.init_kwargs.get("http_options")
        assert http_options is not None, "建立 Client 時必須帶入 http_options"
        assert http_options.timeout == REQUEST_TIMEOUT_MS


def test_get_next_client_is_fast(fake_genai_client):
    """
    量測目前 `_get_next_client()` 的耗時：
    因為是直接從快取的 client 清單裡輪流取用（沒有任何 I/O 或建立物件的動作），
    呼叫 200 次應該要在毫秒等級內完成。
    """
    service = GeminiService(api_keys=["key-a", "key-b"])

    start = time.perf_counter()
    for _ in range(200):
        service._get_next_client()
    duration = time.perf_counter() - start

    print(f"\n[_get_next_client] 呼叫 200 次共花費: {duration * 1000:.3f} ms")
    assert duration < 0.05, "重複取用已快取的 client 應該非常快（<50ms/200次）"
