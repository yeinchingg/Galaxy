"""
app/infrastructure/external_ai/gemini_service.py
外部基礎設施層：對齊當前可用之 Gemini 模型與備援機制
"""

from typing import List, Generator, Union
from google import genai
from google.genai import types
from app.use_cases.interfaces import IAIService

# ✅ 使用帳號實測可用的模型清單，避免 503 塞車與 404 過期問題
GENERATION_MODELS = [
    "gemini-2.5-flash",             # 首選：穩定版 2.5 Flash
    "gemini-flash-lite-latest",      # 備援：最新輕量版 Flash-Lite
    "gemini-flash-latest",           # 備援：最新 Flash 別名
]
EMBEDDING_MODEL = "gemini-embedding-001"

# 單一請求的逾時時間（毫秒）。避免某個 key/模型卡住時，
# 依序重試造成整體對話延遲被無限放大。
REQUEST_TIMEOUT_MS = 15_000


class GeminiService(IAIService):
    def __init__(self, api_keys: Union[str, List[str]], target_dimension: int = 768):
        if isinstance(api_keys, str):
            self.api_keys = [k.strip() for k in api_keys.split(",") if k.strip()]
        elif isinstance(api_keys, list):
            self.api_keys = [str(k).strip() for k in api_keys if str(k).strip()]
        else:
            self.api_keys = []

        if not self.api_keys:
            raise ValueError("未提供有效的 GEMINI_API_KEY！")

        self.current_key_index = 0
        self.embedding_model = EMBEDDING_MODEL
        self.target_dimension = target_dimension

        # 每個 key 各自快取一個 Client，避免每次呼叫都重新建立
        # （省去重複的 client 初始化開銷），並統一套用逾時設定。
        http_options = types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)
        self._clients: List[genai.Client] = [
            genai.Client(api_key=key, http_options=http_options)
            for key in self.api_keys
        ]

    def _get_next_client(self) -> genai.Client:
        client = self._clients[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self._clients)
        return client

    def generate_content(self, prompt: str) -> str:
        last_exception = None
        for model_name in GENERATION_MODELS:
            for _ in range(len(self.api_keys)):
                try:
                    client = self._get_next_client()
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    return response.text.strip()
                except Exception as e:
                    print(f"⚠️ 模型 {model_name} 呼叫失敗 ({e})，切換下一組 Key/模型重試...")
                    last_exception = e
        raise RuntimeError(f"所有模型與 API Key 組合皆失敗: {last_exception}")

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        last_exception = None
        for model_name in GENERATION_MODELS:
            for _ in range(len(self.api_keys)):
                try:
                    client = self._get_next_client()
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=prompt,
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as e:
                    print(f"⚠️ 串流模型 {model_name} 呼叫失敗 ({e})，嘗試切換...")
                    last_exception = e
        yield f"[錯誤] 所有模型與 API Key 組合皆無法完成串流回應: {last_exception}"

    def get_embedding(self, text: str) -> List[float]:
        last_exception = None
        for _ in range(len(self.api_keys)):
            try:
                client = self._get_next_client()
                embed_res = client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                    config={"output_dimensionality": self.target_dimension}
                )
                return embed_res.embeddings[0].values
            except Exception as e:
                print(f"⚠️ Embedding Key 失敗 ({e})，切換重試...")
                last_exception = e
        raise RuntimeError(f"所有 Key 轉換向量皆失敗: {last_exception}")