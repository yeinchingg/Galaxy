"""
tests/unit/test_rag_use_case.py
單元測試：驗證 RAG 應用案例層（相關性門檻過濾、Prompt 切換、歷史記憶）
"""

from unittest.mock import MagicMock
from app.use_cases.rag_chat_use_case import RAGChatUseCase


def test_rag_context_filtering():
    mock_ai = MagicMock()
    mock_ai.get_embedding.return_value = [0.1] * 768
    mock_ai.generate_content.return_value = "主序星核心正在進行氫融合。"

    mock_vdb = MagicMock()
    # 模擬三筆資料：一筆高相關 (0.8)、一筆低相關 (0.4)、一筆雜訊 (0.2)
    mock_vdb.similarity_search.return_value = [
        {"text": "主序星是恆星穩定期", "score": 0.8},
        {"text": "太陽是一顆恆星", "score": 0.4},
        {"text": "無關雜訊文字", "score": 0.2},
    ]

    use_case = RAGChatUseCase(ai_service=mock_ai, vector_store=mock_vdb)
    result = use_case.ask("什麼是主序星？")

    # 驗證只有高於 LOW_RELEVANCE_THRESHOLD (0.35) 的資料會被保留
    assert len(result["contexts"]) == 2
    assert "主序星是恆星穩定期" in result["contexts"]
    assert "無關雜訊文字" not in result["contexts"]
    assert result["grounded"] is True
    assert "主序星" in result["answer"]


def test_rag_fallback_when_no_high_relevance():
    mock_ai = MagicMock()
    mock_ai.get_embedding.return_value = [0.1] * 768
    mock_ai.generate_content.return_value = "回答內容"

    mock_vdb = MagicMock()
    # 沒有高相關資料
    mock_vdb.similarity_search.return_value = [{"text": "邊緣資料", "score": 0.38}]

    use_case = RAGChatUseCase(ai_service=mock_ai, vector_store=mock_vdb)
    result = use_case.ask("未知的物理現象？")

    assert result["grounded"] is False
