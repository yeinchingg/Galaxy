import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_api_endpoint():
    res = client.post("/api/chat", json={"question": "測試問題", "session_id": "test_01"})
    assert res.status_code == 200
    assert "answer" in res.json()