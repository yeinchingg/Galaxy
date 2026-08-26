"""
app/infrastructure/external_ai/pinecone_service.py
外部基礎設施層：實作 Pinecone 向量檢索服務
"""

from typing import List, Dict, Any
from pinecone import Pinecone
from app.domain.interfaces import IVectorStore


class PineconeService(IVectorStore):
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key) if api_key else None
        self.index = self.pc.Index(index_name) if self.pc and index_name else None

    def similarity_search(
        self, vector: List[float], top_k: int = 3
    ) -> List[Dict[str, Any]]:
        if not self.index:
            return []
        try:
            query_res = self.index.query(
                vector=vector, top_k=top_k, include_metadata=True
            )
            results = []
            for match in query_res.matches:
                if match.metadata and "text" in match.metadata:
                    results.append(
                        {
                            "text": match.metadata["text"].strip(),
                            "score": getattr(match, "score", 0.0) or 0.0,
                        }
                    )
            return results
        except Exception as e:
            print(f"Pinecone 檢索失敗: {e}")
            return []
