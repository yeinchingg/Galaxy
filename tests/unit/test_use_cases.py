import pytest
from unittest.mock import AsyncMock
from app.use_cases.rag_chat_use_case import RAGChatUseCase

@pytest.mark.asyncio
async def test_rag_chat_flow():
    mock_ai = AsyncMock()
    mock_ai.generate_chat_response.return_value = "赫羅圖橫軸代表表面溫度。"
    mock_vector = AsyncMock()
    mock_vector.similarity_search.return_value = ["赫羅圖相關文獻"]
    mock_repo = AsyncMock()

    use_case = RAGChatUseCase(ai_service=mock_ai, vector_store=mock_vector, repository=mock_repo)
    result = await use_case.execute("什麼是赫羅圖？", "session_123")

    assert "赫羅圖" in result
    mock_vector.similarity_search.assert_called_once_with("什麼是赫羅圖？", top_k=2)
    mock_ai.generate_chat_response.assert_called_once()
    mock_repo.save_session.assert_called_once()