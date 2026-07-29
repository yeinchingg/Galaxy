import os
import random
from typing import Generator, List, Dict, Any
from google import genai
from pinecone import Pinecone


class AstronomyRAGEngine:
    def __init__(self, gemini_api_key: str, pinecone_api_key: str, index_name: str, target_dimension: int = 768):
        # 1. 解析多組 Gemini API Key (自動切分並清理空白)
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

        # 2. 初始化 Pinecone
        self.pc = Pinecone(
            api_key=pinecone_api_key) if pinecone_api_key else None
        self.index = self.pc.Index(
            index_name) if self.pc and index_name else None

    def _get_next_client(self) -> genai.Client:
        """取得當前輪播的 Gemini Client，並將指針移至下一組"""
        current_key = self.api_keys[self.current_key_index]
        self.current_key_index = (
            self.current_key_index + 1) % len(self.api_keys)
        return genai.Client(api_key=current_key)

    def _execute_with_retry(self, func):
        """通用自動重試機制：若遇到 401 或 API 失敗，自動切換下一組 Key"""
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
        """包覆輪播機制的向量轉換方法 (修復 401 崩潰點)"""
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

    def retrieve_context(self, question: str, top_k: int = 3) -> List[str]:
        """從 Pinecone 檢索相關上下文"""
        if not self.index:
            return []
        try:
            # 呼叫帶有輪播機制的 _get_embedding
            query_vector = self._get_embedding(question)

            # Pinecone 查詢
            query_res = self.index.query(
                vector=query_vector, top_k=top_k, include_metadata=True)
            contexts = []
            for match in query_res.matches:
                if match.metadata and "text" in match.metadata:
                    contexts.append(match.metadata["text"])
            return contexts
        except Exception as e:
            print(f"檢索失敗: {e}")
            return []

    def ask(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """單次問答"""
        try:
            contexts = self.retrieve_context(question, top_k=top_k)
            context_str = "\n".join(contexts)
            prompt = f"請根據以下參考資訊回答問題。\n參考資訊：\n{context_str}\n\n問題：{question}"

            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return {"status": "success", "answer": response.text, "contexts": contexts}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ask_topic(self, question: str, topic: str, top_k: int = 3) -> Dict[str, Any]:
        """特定主題問答"""
        try:
            contexts = self.retrieve_context(
                f"[{topic}] {question}", top_k=top_k)
            context_str = "\n".join(contexts)
            prompt = f"主題：{topic}\n參考資料：\n{context_str}\n\n問題：{question}"

            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return {"status": "success", "answer": response.text, "contexts": contexts}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_stream(self, question: str, contexts: List[str]) -> Generator[str, None, None]:
        """串流生成 (以 Chunk 回傳)"""
        context_str = "\n".join(contexts)
        prompt = f"請根據以下參考資訊回答問題。\n參考資訊：\n{context_str}\n\n問題：{question}"

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
        """生成簡短提示"""
        try:
            prompt = f"請根據以下狀態描述，產生一句簡短的旁白解說 (30字以內)：\n{description}"
            response = self._execute_with_retry(
                lambda client: client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
            )
            return response.text.strip()
        except Exception as e:
            return "無法取得動態旁白。"
