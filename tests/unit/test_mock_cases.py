"""Mock 測試：對應 SL-TC-AI-02、SL-TC-AI-10、SL-TC-LB-16（GeminiService 部分）、題庫格式檢查。
不需要真的 Gemini / Pinecone 金鑰，也不需要網路。
放在 tests/unit/，在專案根目錄執行：python -m pytest tests/unit/test_mock_cases.py -v
"""
import sys, types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# ---- 以假的 google.genai 取代真實 SDK（必須在 import GeminiService 之前）----
class FakeModels:
    def __init__(self, key, log):
        self.key, self.log = key, log

    def generate_content(self, model, contents):
        self.log.append(("content", self.key, model))
        if self.key.startswith("bad"):
            raise RuntimeError("invalid api key")
        return types.SimpleNamespace(text=f"  ok-from-{self.key}  ")

    def generate_content_stream(self, model, contents):
        self.log.append(("stream", self.key, model))
        if self.key.startswith("bad"):
            raise RuntimeError("invalid api key")
        return iter([types.SimpleNamespace(text="你"), types.SimpleNamespace(text="好")])


CALL_LOG = []

class FakeClient:
    def __init__(self, api_key, http_options=None):
        self.models = FakeModels(api_key, CALL_LOG)

fake_genai = types.ModuleType("google.genai")
fake_genai.Client = FakeClient
fake_types = types.ModuleType("google.genai.types")
fake_types.HttpOptions = lambda **kw: kw
fake_genai.types = fake_types
fake_google = types.ModuleType("google")
fake_google.genai = fake_genai
sys.modules.update({"google": fake_google, "google.genai": fake_genai, "google.genai.types": fake_types})

from app.infrastructure.external_ai.gemini_service import GeminiService  # noqa: E402
from app.use_cases.rag_chat_use_case import RAGChatUseCase  # noqa: E402


# ======================= SL-TC-AI-02 相關性閾值邊界 =======================
class FakeAI:
    def get_embedding(self, text):
        return [0.0]

class FakeStore:
    def __init__(self, items):
        self.items = items
    def similarity_search(self, vector, top_k=3):
        return self.items

def test_ai_02_relevance_threshold_boundaries():
    items = [
        {"text": "A", "score": 0.55},
        {"text": "B", "score": 0.549},
        {"text": "C", "score": 0.35},
        {"text": "D", "score": 0.349},
    ]
    uc = RAGChatUseCase(FakeAI(), FakeStore(items))
    got = {r["text"]: r["relevance"] for r in uc.retrieve_context("q", top_k=4)}
    assert got == {"A": "high", "B": "low", "C": "low"}   # D(0.349) 被捨棄

def test_ai_02_results_sorted_and_deduplicated():
    items = [{"text": "X", "score": 0.4}, {"text": "Y", "score": 0.9}, {"text": "X", "score": 0.8}]
    uc = RAGChatUseCase(FakeAI(), FakeStore(items))
    res = uc.retrieve_context("q")
    assert [r["text"] for r in res] == ["Y", "X"]          # 依分數由高到低，重複文字只留第一筆

def test_ai_02_only_low_relevance_uses_no_context_template():
    uc = RAGChatUseCase(FakeAI(), FakeStore([{"text": "L", "score": 0.4}]))
    prompt = uc.build_prompt("q", uc.retrieve_context("q"))
    assert "知識庫裡沒有找到" in prompt


# ======================= SL-TC-AI-10 金鑰輪替 =======================
def test_ai_10_rotates_to_second_key_on_failure():
    CALL_LOG.clear()
    svc = GeminiService("bad1,good2")
    assert svc.generate_content("hi") == "ok-from-good2"   # 回傳會 strip
    keys = [k for _, k, _ in CALL_LOG]
    assert keys[0] == "bad1" and keys[-1] == "good2"

def test_ai_10_stream_rotates_to_second_key():
    CALL_LOG.clear()
    svc = GeminiService("bad1,good2")
    assert "".join(svc.generate_stream("hi")) == "你好"

def test_ai_10_no_key_raises():
    try:
        GeminiService("")
    except ValueError:
        return
    raise AssertionError("沒有金鑰應該丟出 ValueError（SL-FR-DS-05）")


# ======================= SL-TC-LB-16 全部失敗（服務層）=======================
def test_lb_16_all_keys_fail_stream_yields_error_message():
    CALL_LOG.clear()
    svc = GeminiService("bad1,bad2")
    chunks = list(svc.generate_stream("hi"))
    assert len(chunks) == 1 and chunks[0].startswith("[錯誤]")
    # 3 個模型 x 2 把 Key 都試過
    assert len(CALL_LOG) == 6

def test_lb_16_all_keys_fail_generate_content_raises():
    svc = GeminiService("bad1")
    try:
        svc.generate_content("hi")
    except RuntimeError:
        return
    raise AssertionError("全部失敗應丟出 RuntimeError")

def test_narrate_falls_back_when_ai_fails():
    class Boom:
        def generate_content(self, p):
            raise RuntimeError("x")
    assert RAGChatUseCase(Boom()).generate_short_hint("desc") == "無法取得動態旁白。"


# ======================= 題庫格式檢查（發現的缺陷）=======================
def test_quiz_every_question_has_question_correct_and_three_wrongs():
    from app.infrastructure.quiz import QUESTIONS
    bad = []
    for level, pool in QUESTIONS.items():
        for i, item in enumerate(pool):
            ok = (len(item) == 3 and isinstance(item[2], (list, tuple))
                  and len(item[2]) == 3 and item[1] not in item[2])
            if not ok:
                bad.append((level, i, str(item[0])[:20]))
    assert not bad, f"題庫格式錯誤（會讓 /api/quiz/start 回 500）：{bad}"
