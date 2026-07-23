# rag_engine.py
import os
from google import genai
from google.genai import types
from pinecone import Pinecone


class AstronomyRAGEngine:

    def __init__(self, gemini_api_key: str, pinecone_api_key: str, index_name: str,
                 # text-embedding-004 已於 2026/1/14 停用
                 embedding_model: str = "gemini-embedding-001",
                 generation_model: str = "gemini-flash-latest",  # 別名，Google 會自動指向目前最新的 Flash 模型
                 target_dimension: int = 768):

        self.embedding_model = embedding_model
        self.generation_model = generation_model
        self.target_dimension = target_dimension

        self.client = genai.Client(api_key=gemini_api_key)

        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(index_name)

    def _get_embedding(self, text: str) -> list:
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.target_dimension)
            )
            vector = response.embeddings[0].values
            return vector
        except Exception as e:
            raise Exception(f"向量轉換失敗: {str(e)}")

    def retrieve_context(self, question: str, top_k: int = 3) -> list:
        query_vector = self._get_embedding(question)
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        retrieved_items = []
        for match in results.get("matches", []):
            retrieved_items.append({
                "text": match["metadata"]["text"],
                "source": match["metadata"]["source"],
                "score": round(match["score"], 4)
            })
        return retrieved_items

    def generate_answer(self, question: str, retrieved_items: list) -> str:
        context_blocks = []
        for idx, item in enumerate(retrieved_items):
            context_blocks.append(
                f"[文獻 {idx+1} | 來源: {item['source']}]\n{item['text']}")
        context_str = "\n\n---\n\n".join(context_blocks)

        prompt = f"""你是一位專業的天文學專家。請根據下方提供的【參考文獻】回答使用者的【問題】。
若文獻中無相關資訊，請回答「根據現有知識庫資料無法回答此問題」，不可胡亂虛構。

【參考文獻】：
{context_str}

【問題】：
{question}

請詳細且條理清晰地回答："""

        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"❌ 【新版 SDK 報錯】: {str(e)}"

    def generate_stream(self, question: str, retrieved_items: list):
        """跟 generate_answer 一樣的 prompt，但用串流方式一段一段吐出文字"""
        context_blocks = []
        for idx, item in enumerate(retrieved_items):
            context_blocks.append(
                f"[文獻 {idx+1} | 來源: {item['source']}]\n{item['text']}")
        context_str = "\n\n---\n\n".join(context_blocks)

        prompt = f"""你是一位專業的天文學專家。請根據下方提供的【參考文獻】回答使用者的【問題】。
若文獻中無相關資訊，請回答「根據現有知識庫資料無法回答此問題」，不可胡亂虛構。

【參考文獻】：
{context_str}

【問題】：
{question}

請詳細且條理清晰地回答："""

        stream = self.client.models.generate_content_stream(
            model=self.generation_model,
            contents=prompt,
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text

    # 主題限定問答：*1~*3 這幾個固定主題，各自給一段系統提示詞把回答方向收斂住
    TOPIC_PROMPTS = {
        "physics_meaning": "請聚焦在恆星物理量的意義：顏色與溫度的關係、自轉速度對形狀的影響、金屬量對顏色的影響。",
        "star_lifecycle": "請聚焦在恆星從誕生、主序星、演化到死亡（白矮星/中子星/黑洞）的整個生命週期。",
        "chat": "請自由回答使用者的天文相關問題。",
    }

    def ask_topic(self, question: str, topic: str, top_k: int = 3) -> dict:
        """跟 ask() 一樣，但依 topic 加上不同的引導提示詞，讓回答聚焦在該主題"""
        topic_instruction = self.TOPIC_PROMPTS.get(
            topic, self.TOPIC_PROMPTS["chat"])
        try:
            retrieved = self.retrieve_context(question, top_k=top_k)
            context_blocks = [
                f"[文獻 {i+1} | 來源: {item['source']}]\n{item['text']}"
                for i, item in enumerate(retrieved)
            ]
            context_str = "\n\n---\n\n".join(
                context_blocks) if context_blocks else "（查無相關文獻）"

            prompt = f"""你是一位專業的天文學專家。{topic_instruction}
請根據下方【參考文獻】回答【問題】，若無相關資訊請誠實告知，不可胡亂虛構。

【參考文獻】：
{context_str}

【問題】：
{question}

請詳細且條理清晰地回答："""

            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt,
            )
            return {
                "status": "success",
                "topic": topic,
                "question": question,
                "answer": response.text,
                "sources": list(set(item["source"] for item in retrieved)),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_short_hint(self, context_description: str) -> str:
        """
        給恆星模擬滑桿 / 3D 投影用：輸入目前畫面的數值狀態描述，
        回傳一句簡短的自然語言提示（不做 RAG 檢索，純生成，速度快）。
        前端請做 debounce（使用者停止拖曳滑桿一段時間後才呼叫），避免過度呼叫。
        """
        prompt = f"""你是天文教學助理。以下是使用者目前互動畫面的數值狀態：
{context_description}

請用一句話（30字以內、繁體中文、口語化）向使用者說明這個畫面現在呈現的重點是什麼，不要條列、不要客套話。"""
        try:
            response = self.client.models.generate_content(
                model=self.generation_model,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            return f"（提示生成失敗：{e}）"

    def ask(self, question: str, top_k: int = 3) -> dict:
        try:
            retrieved = self.retrieve_context(question, top_k=top_k)
            if not retrieved:
                return {
                    "status": "success",
                    "question": question,
                    "answer": "您的資料庫中目前沒有任何相關的內容喔！",
                    "sources": [],
                    "raw_retrieved": []
                }

            answer = self.generate_answer(question, retrieved)
            sources = list(set([item["source"] for item in retrieved]))

            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "sources": sources,
                "raw_retrieved": retrieved
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
