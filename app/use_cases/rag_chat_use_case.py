"""
app/use_cases/rag_chat_use_case.py
應用案例層：RAG 對話引擎（相關性過濾、Prompt 模板裝配、歷史記憶協調）
"""

from typing import Generator, List, Dict, Any, Optional
from app.use_cases.interfaces import IAIService, IVectorStore, ISessionRepository

# 相關性分數門檻
HIGH_RELEVANCE_THRESHOLD = 0.55
LOW_RELEVANCE_THRESHOLD = 0.35
HISTORY_TURNS = 4

SYSTEM_PERSONA = """你是一位親切、耐心的天文助教，正在跟一位對天文有興趣的學習者聊天。

回答規則：
- 用口語、自然的中文回答，像在跟朋友解釋一樣，不要條列「根據參考資訊」這種制式開場白。
- 先用 1-2 句話直接回答重點，再視需要補充細節或舉例。
- 適度使用類比（例如把恆星演化比喻成生命階段）幫助理解，但不要每句都硬塞比喻。
- 如果使用者是接續前面的話題發問，要延續脈絡，不要重新自我介紹或重複前面講過的內容。
- 段落不要太長，重要數字或結論可以用簡短的一行帶出來。
"""

HAS_CONTEXT_TEMPLATE = """{persona}

以下是從知識庫中找到、與問題高度相關的資料，請「消化吸收後用自己的話」回答，
不要逐字複製，也不要出現「根據參考資訊」這種字眼：
---
{context}
---

{history_block}使用者的問題：{question}
"""

NO_CONTEXT_TEMPLATE = """{persona}

知識庫裡沒有找到跟這個問題直接相關的資料。請誠實地用你自己的天文知識回答，
並在回答的最後很自然地補一句，說明這部分不是來自課程知識庫、建議使用者可以再確認一下（不要用制式警語語氣）。
如果使用者的問題比較模糊或籠統，也可以順口建議一種更具體的問法（例如指定恆星名稱、參數或現象），
幫助之後的提問更容易命中知識庫，但不要每次都硬加這句，只有在真的有幫助時才提。

{history_block}使用者的問題：{question}
"""

HINT_TEMPLATE = """請根據以下狀態描述，用親切、像旁白解說的口吻產生一句簡短提示（30 字以內，不要條列、不要加引號）：
{description}
"""


class RAGChatUseCase:
    def __init__(self, ai_service: IAIService, vector_store: Optional[IVectorStore] = None, session_repo: Optional[ISessionRepository] = None):
        self.ai_service = ai_service
        self.vector_store = vector_store
        self.session_repo = session_repo

    def retrieve_context(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.vector_store:
            return []

        query_vector = self.ai_service.get_embedding(question)
        raw_matches = self.vector_store.similarity_search(query_vector, top_k=top_k)

        results = []
        seen_texts = set()
        for item in raw_matches:
            text = item.get("text", "")
            score = item.get("score", 0.0)
            if not text or text in seen_texts or score < LOW_RELEVANCE_THRESHOLD:
                continue

            seen_texts.add(text)
            results.append({
                "text": text,
                "score": score,
                "relevance": "high" if score >= HIGH_RELEVANCE_THRESHOLD else "low"
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def _build_history_block(self, session_id: Optional[str]) -> str:
        if not session_id or not self.session_repo:
            return ""
        try:
            history = self.session_repo.get_history(session_id)
            if not history:
                return ""
            recent = history[-HISTORY_TURNS * 2:]
            lines = [
                f"{'使用者' if m.get('role') == 'user' else '助教'}：{m.get('content', '')}"
                for m in recent
            ]
            return "先前的對話紀錄：\n" + "\n".join(lines) + "\n\n"
        except Exception:
            return ""

    def build_prompt(self, question: str, contexts: List[Dict[str, Any]], session_id: Optional[str] = None) -> str:
        history_block = self._build_history_block(session_id)
        high = [c for c in contexts if c.get("relevance") == "high"]

        if high:
            context_text = "\n\n".join(f"- {c['text']}" for c in high)
            return HAS_CONTEXT_TEMPLATE.format(
                persona=SYSTEM_PERSONA,
                context=context_text,
                history_block=history_block,
                question=question,
            )
        else:
            return NO_CONTEXT_TEMPLATE.format(
                persona=SYSTEM_PERSONA,
                history_block=history_block,
                question=question,
            )

    def ask(self, question: str, top_k: int = 3, session_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            contexts = self.retrieve_context(question, top_k=top_k)
            prompt = self.build_prompt(question, contexts, session_id)
            answer = self.ai_service.generate_content(prompt)

            if session_id and self.session_repo:
                self.session_repo.save_message(session_id, "user", question)
                self.session_repo.save_message(session_id, "ai", answer)

            return {
                "status": "success",
                "answer": answer,
                "contexts": [c["text"] for c in contexts],
                "grounded": any(c["relevance"] == "high" for c in contexts),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_stream(self, question: str, top_k: int = 3, session_id: Optional[str] = None) -> Generator[str, None, None]:
        contexts = self.retrieve_context(question, top_k=top_k)
        prompt = self.build_prompt(question, contexts, session_id)
        return self.ai_service.generate_stream(prompt)

    def generate_short_hint(self, description: str) -> str:
        try:
            prompt = HINT_TEMPLATE.format(description=description)
            return self.ai_service.generate_content(prompt)
        except Exception:
            return "無法取得動態旁白。"