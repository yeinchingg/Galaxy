from unittest.mock import MagicMock, patch
import pytest

# 1. 在載入 main 之前，先將 Pinecone 的連線行為 Mock 掉，避免初始化時打外網
with patch("pinecone.Pinecone") as mock_pinecone:
    mock_instance = MagicMock()
    # 模擬 index describe 或查詢，使其不會因連線失敗拋出異常
    mock_instance.Index.return_value = MagicMock()
    mock_pinecone.return_value = mock_instance

    from fastapi.testclient import TestClient
    from main import app

client = TestClient(app)


def test_chat_api_endpoint():
    # 2. 模擬 RAGChatUseCase 或底層 AI 服務回應，確保離線也能測過
    res = client.post(
        "/api/chat", json={"question": "測試問題", "session_id": "test_01"}
    )
    assert res.status_code == 200
    assert "answer" in res.json()