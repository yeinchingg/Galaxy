import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_system_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_daily_knowledge_format():
    response = client.get("/api/daily-knowledge")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    if data["data"]:
        first_item = data["data"][0]
        assert "title" in first_item
        assert "url" in first_item
        assert "image_url" in first_item

def test_user_tracking():
    payload = {
        "user_id": "test_user_123",
        "topic": "black_hole",
        "action": "click",
        "params": {}
    }
    response = client.post("/api/track", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "tracked"