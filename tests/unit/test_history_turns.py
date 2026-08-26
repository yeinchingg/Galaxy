"""
tests/unit/test_history_turns.py
驗證 HISTORY_TURNS 設定值，以及 _build_history_block 的實際行為與耗時。
"""

from unittest.mock import MagicMock

from app.use_cases import rag_chat_use_case as rag_module
from app.use_cases.rag_chat_use_case import RAGChatUseCase


def _make_long_history(turns: int = 10):
    """建立一份很長的歷史紀錄（10 輪、20 則訊息）。"""
    history = []
    for i in range(turns):
        history.append({"role": "user", "content": f"這是第 {i} 輪的使用者問題內容"})
        history.append({"role": "ai", "content": f"這是第 {i} 輪的助教回答內容"})
    return history


def test_history_turns_is_set_to_two():
    """回歸測試：確保 HISTORY_TURNS 沒有被不小心改回 4 或更大。"""
    assert rag_module.HISTORY_TURNS == 2


def test_history_block_only_includes_last_two_turns():
    """驗證 _build_history_block 實際只截取最近 HISTORY_TURNS 輪對話。"""
    mock_repo = MagicMock()
    mock_repo.get_history.return_value = _make_long_history(turns=10)

    use_case = RAGChatUseCase(ai_service=MagicMock(), session_repo=mock_repo)
    block = use_case._build_history_block("session_1")

    # HISTORY_TURNS=2 → 最近 2 輪 = 4 則訊息
    # 排除開頭的「先前的對話紀錄：」標題行，只數實際訊息行
    message_lines = [
        line
        for line in block.split("\n")
        if line.startswith("使用者：") or line.startswith("助教：")
    ]
    expected_lines = 2 * rag_module.HISTORY_TURNS
    assert len(message_lines) == expected_lines

    # 應該只包含最新的內容（第 8、9 輪），不該出現最早的第 0 輪內容
    assert "第 9 輪" in block
    assert "第 0 輪" not in block


def test_build_history_block_timing_and_size():
    """
    單純量測目前 _build_history_block 的耗時與輸出字元數，
    不跟任何其他設定比較。
    """
    import time

    mock_repo = MagicMock()
    mock_repo.get_history.return_value = _make_long_history(turns=10)
    use_case = RAGChatUseCase(ai_service=MagicMock(), session_repo=mock_repo)

    start = time.perf_counter()
    block = use_case._build_history_block("session_1")
    duration = time.perf_counter() - start

    print(
        f"\n[_build_history_block] 耗時: {duration * 1000:.3f} ms | "
        f"輸出長度: {len(block)} 字元"
    )
    assert isinstance(block, str)
