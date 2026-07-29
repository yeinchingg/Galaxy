import os
from typing import Generator, List, Dict, Any, Optional
from google import genai
from pinecone import Pinecone

# ============================================================
# 人性化回答的核心設計說明
# ------------------------------------------------------------
# 這不是單純多寫一句 "請用親切的語氣回答"。
# 而是把 RAG pipeline 拆成三個獨立、可各自調整的環節：
#
#   1. retrieve_context()  -> 依相關性分數分級、過濾雜訊、去重
#   2. _build_prompt()     -> 依「有沒有查到資料」+「對話歷史」
#                              動態組出不同的 prompt 模板
#   3. persona 模板         -> 語氣/格式規則集中管理，不散落各處
#
# 之後要調整語氣、格式、fallback 話術，只需要改
# SYSTEM_PERSONA / NO_CONTEXT_TEMPLATE 這些常數，
# 不用去改每一支呼叫 API 的函式。
# ============================================================


# 相關性分數門檻（Pinecone cosine 相似度，依你的 embedding 模型調整）
HIGH_RELEVANCE_THRESHOLD = 0.55
LOW_RELEVANCE_THRESHOLD = 0.35

# 記憶要帶入 prompt 的最近幾輪對話
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


class AstronomyRAGEngine:
    def __init__(self, gemini_api_key: str, pinecone_api_key: str, index_name: str,
                 target_dimension: int = 768, storage_module=None):
        if isinstance(gemini_api_key, str):
            self.api_keys = [k.strip()
                             for k in gemini_api_key.split(",") if k.strip()]
        elif isinstance(gemini_api_key, list):
            self.api_keys = [str(k).strip()
                             for k in gemini_api_key if str(k).strip()]
        else:
            self.api_keys = []

        if not self.api_keys:
            raise ValueError("未提供有效的 GEMINI_API_KEY！")

        self.current_key_index = 0
        self.embedding_model = "text-embedding-004"
        self.target_dimension = target_dimension

        self.pc = Pinecone(
            api_key=pinecone_api_key) if pinecone_api_key else None
        self.index = self.pc.Index(
            index_name) if self.pc and index_name else None

        # 可選：注入 storage module，用來讀對話歷史做「記憶」
        self.storage = storage_module

    # ---------------- Gemini Key 輪播機制 ----------------

    def _get_next_client(self) -> genai.Client:
        current_key = self.api_keys[self.current_key_index]
        self.current_key_index = (
            self.current_key_index + 1) % len(self.api_keys)
        return genai.Client(api_key=current_key)

    def _execute_with_retry(self, func):
        last_exception = None
        for _ in range(len(self.api_keys)):
            try:
                client = self._get_next_client()
                return func(client)
            except Exception as e:
                print(f"⚠️ Gemini API Key 呼叫失敗 ({e})，正在自動切換下一組 API Key 重試...")
                last_exception = e
        raise RuntimeError(f"所有 Gemini API Keys 皆無效或呼叫失敗: {last_exception}")

    def _get_embedding(self, text: str) -> List[float]:
        try:
            embed_res = self._execute_with_retry(
                lambda client: client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config={"output_dimensionality": self.target_dimension}
                )
            )
            return embed_res.embedding.values
        except Exception as e:
            print(f"❌ 所有 Key 轉換向量皆失敗: {e}")
            raise e

    # ---------------- 檢索：分級 + 過濾 + 去重 ----------------

    def retrieve_context(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        回傳格式改為 List[Dict]，而不是 List[str]：
        [{"text": ..., "score": ..., "relevance": "high"/"low"}, ...]
        呼叫端可以依照 relevance 決定要不要用、要怎麼用。
        只過濾掉分數低於 LOW_RELEVANCE_THRESHOLD 的雜訊片段。
        """
        if not self.index:
            return []
        try:
            query_vector = self._get_embedding(question)
            query_res = self.index.query(
                vector=query_vector, top_k=top_k, include_metadata=True)

            results = []
            seen_texts = set()
            for match in query_res.matches:
                if not match.metadata or "text" not in match.metadata:
                    continue
                text = match.metadata["text"].strip()
                if not text or text in seen_texts:
                    continue
                score = getattr(match, "score", 0.0) or 0.0
                if score < LOW_RELEVANCE_THRESHOLD:
                    continue  # 太不相關，直接丟棄，不讓它污染 prompt

                seen_texts.add(text)
                results.append({
                    "text": text,
                    "score": score,
                    "relevance": "high" if score >= HIGH_RELEVANCE_THRESHOLD else "low",
                })

            # 分數高的排前面
            results.sort(key=lambda r: r["score"], reverse=True)
            return results
        except Exception as e:
            print(f"檢索失敗: {e}")
            return []

    @staticmethod
    def _contexts_to_text(contexts: List[Dict[str, Any]]) -> str:
        return "\n\n".join(f"- {c['text']}" for c in contexts)

    # ---------------- 對話歷史（記憶） ----------------

    def _build_history_block(self, session_id: Optional[str]) -> str:
        if not session_id or not self.storage:
            return ""
        try:
            history = self.storage.get_history(session_id)
        except Exception:
            return ""
        if not history:
            return ""

        recent = history[-HISTORY_TURNS * 2:]
        lines = []
        for msg in recent:
            role = "使用者" if msg["role"] == "user" else "助教"
            lines.append(f"{role}：{msg['content']}")
        return "先前的對話紀錄：\n" + "\n".join(lines) + "\n\n"

    # ---------------- Prompt 組裝 ----------------

    def _build_prompt(self, question: str, contexts: List[Dict[str, Any]],
                      session_id: Optional[str] = None) -> str:
        history_block = self._build_history_block(session_id)
        # 只用「高相關」的片段作為主要依據；若完全沒有高相關片段，
        # 就切換成「誠實 fallback」模板，不硬套資料庫話術。
        high = [c for c in contexts if c["relevance"] == "high"]

        if high:
            return HAS_CONTEXT_TEMPLATE.format(
                persona=SYSTEM_PERSONA,
                context=self._contexts_to_text(high),
                history_block=history_block,
                question=question,
            )
        else:
            return NO_CONTEXT_TEMPLATE.format(
                persona=SYSTEM_PERSONA,
                history_block=history_block,
                question=question,
            )

    # ---------------- 對外 API ----------------

    def ask(self, question: str, top_k: int = 3, session_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            contexts = self.retrieve_context(question, top_k=top_k)
            prompt = self._build_prompt(question, contexts, session_id)

            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return {
                "status": "success",
                "answer": response.text.strip(),
                "contexts": [c["text"] for c in contexts],
                "grounded": any(c["relevance"] == "high" for c in contexts),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask_topic(self, question: str, topic: str, top_k: int = 3,
                  session_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            contexts = self.retrieve_context(
                f"[{topic}] {question}", top_k=top_k)
            prompt = self._build_prompt(question, contexts, session_id)

            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return {
                "status": "success",
                "answer": response.text.strip(),
                "contexts": [c["text"] for c in contexts],
                "grounded": any(c["relevance"] == "high" for c in contexts),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_stream(self, question: str, contexts: List[Dict[str, Any]],
                        session_id: Optional[str] = None) -> Generator[str, None, None]:
        prompt = self._build_prompt(question, contexts, session_id)

        last_exception = None
        for _ in range(len(self.api_keys)):
            try:
                client = self._get_next_client()
                response_stream = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                print(f"⚠️ 串流 API Key 呼叫失敗 ({e})，嘗試切換下一組 Key...")
                last_exception = e

        yield f"[錯誤] 所有 API Key 皆無法完成串流回應: {last_exception}"

    def generate_short_hint(self, description: str) -> str:
        try:
            prompt = HINT_TEMPLATE.format(description=description)
            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return response.text.strip()
        except Exception as e:
            return "無法取得動態旁白。"
