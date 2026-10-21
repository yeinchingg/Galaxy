"""
tests/unit/test_mock_cases.py
單元測試：驗證 GeminiService 的 API Key 輪替、降級機制與全部失敗時的錯誤捕捉。

包含：
1. 單次問答中，第 1 組 Key 失敗時自動切換至第 2 組 Key (SL-TC-AI-10)。
2. 串流問答中，第 1 組 Key 失敗時自動切換至第 2 組 Key 串流。
3. 當所有 Key 與模型全部失敗時，嘗試完整輪替次數並回傳錯誤訊息 (SL-TC-LB-16)。
"""

import importlib
import pytest
from unittest.mock import MagicMock
from app.infrastructure.external_ai import gemini_service as gs_module
from app.infrastructure.external_ai.gemini_service import GeminiService


@pytest.fixture(autouse=True)
def clean_gemini_environment(monkeypatch):
    """
    環境隔離 Fixture：
    每次測試前重新載入 gemini_service 模組，避免被其他測試檔案的全域 monkeypatch 殘留污染。
    """
    importlib.reload(gs_module)
    yield
    importlib.reload(gs_module)


def test_ai_10_rotates_to_second_key_on_failure(monkeypatch):
    """
    驗證單次問答在第 1 組金鑰失效時自動輪替到第 2 組金鑰 (SL-TC-AI-10)
    """
    # 建立兩個獨立的 Client Mock：第一個拋錯，第二個成功回應
    mock_client_fail = MagicMock()
    mock_client_fail.models.generate_content.side_effect = Exception("400 INVALID_ARGUMENT API key expired")

    mock_client_success = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "恆星演化回答"
    mock_client_success.models.generate_content.return_value = mock_response

    clients = [mock_client_fail, mock_client_success]

    # 當 GeminiService 初始化建立 Client 時依序分配
    def client_factory(**kwargs):
        if clients:
            return clients.pop(0)
        return MagicMock()

    monkeypatch.setattr(gs_module.genai, "Client", client_factory)

    # 實例化包含 2 組 Key 的服務
    service = gs_module.GeminiService(api_keys=["invalid-key-1", "valid-key-2"])

    # 執行內容生成
    result = service.generate_content("請說明太陽演化")

    assert result == "恆星演化回答"
    mock_client_fail.models.generate_content.assert_called()
    mock_client_success.models.generate_content.assert_called()


def test_ai_10_stream_rotates_to_second_key(monkeypatch):
    """
    驗證串流問答在第 1 組金鑰失敗時輪替到第 2 組金鑰正常產生串流 Chunk
    """
    # 第一個 Client 串流拋出異常
    mock_client_fail = MagicMock()
    mock_client_fail.models.generate_content_stream.side_effect = Exception("400 API key invalid")

    # 第二個 Client 正常回傳串流資料包
    mock_client_success = MagicMock()
    mock_chunk = MagicMock()
    mock_chunk.text = "你好"
    mock_client_success.models.generate_content_stream.return_value = [mock_chunk]

    clients = [mock_client_fail, mock_client_success]

    def client_factory(**kwargs):
        if clients:
            return clients.pop(0)
        return MagicMock()

    monkeypatch.setattr(gs_module.genai, "Client", client_factory)

    service = gs_module.GeminiService(api_keys=["invalid-key", "valid-key"])

    # 呼叫串流產生器並轉成文字列表
    chunks = list(service.generate_stream("測試問題"))
    combined_text = "".join(chunks)

    assert combined_text == "你好"


def test_lb_16_all_keys_fail_stream_yields_error_message(monkeypatch):
    """
    驗證當所有金鑰與模型組合皆失敗時，重試總次數達到預期（2 Keys * 3 Models = 6 次）
    並回傳帶有 [錯誤] 標籤的訊息 (SL-TC-LB-16)
    """
    call_count = 0

    def mock_stream_always_fails(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise Exception("API Quota Exceeded")

    # 建立一個統一累計調用次數的假 Client
    fake_client = MagicMock()
    fake_client.models.generate_content_stream.side_effect = mock_stream_always_fails

    monkeypatch.setattr(gs_module.genai, "Client", lambda **kwargs: fake_client)

    # 2 組 Key，系統預設輪替 3 個模型，合計需嘗試 6 次
    service = gs_module.GeminiService(api_keys=["key-1", "key-2"])

    chunks = list(service.generate_stream("測試提問"))
    output = "".join(chunks)

    # 驗證 6 次重試均被執行且輸出錯誤提示
    assert call_count == 6
    assert "[錯誤]" in output