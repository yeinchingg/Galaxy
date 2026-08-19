from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional


class IAIService(ABC):
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass


class IVectorStore(ABC):
    @abstractmethod
    def similarity_search(self, vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        pass


class IDataRepository(ABC):
    @abstractmethod
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str) -> None:
        pass

    @abstractmethod
    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> None:
        pass


ISessionRepository = IDataRepository