from unittest.mock import MagicMock
from app.use_cases.rag_chat_use_case import RAGChatUseCase


def test_rag_chat_flow():
    mock_ai = MagicMock()
    mock_ai.get_embedding.return_value = [0.1]
    mock_ai.generate_content.return_value = "赫羅圖橫軸代表表面溫度。"
    mock_vector = MagicMock()
    mock_vector.similarity_search.return_value = [
        {"text": "赫羅圖相關文獻", "score": 0.8}
    ]
    mock_repo = MagicMock()
    mock_repo.get_history.return_value = []

    use_case = RAGChatUseCase(
        ai_service=mock_ai, vector_store=mock_vector, session_repo=mock_repo
    )
    result = use_case.ask("什麼是赫羅圖？", top_k=2, session_id="session_123")

    assert result["status"] == "success"
    assert "赫羅圖" in result["answer"]
    assert result["grounded"] is True
    mock_vector.similarity_search.assert_called_once_with([0.1], top_k=2)
    mock_ai.generate_content.assert_called_once()
    assert mock_repo.save_message.call_count == 2  # 使用者與助理各一筆