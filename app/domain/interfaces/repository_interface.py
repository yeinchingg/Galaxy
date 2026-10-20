from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator, Optional


class IDataRepository(ABC):
    @abstractmethod
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def save_message(
        self, session_id: str, role: str, content: str, user_id: int = 1
    ) -> None:
        pass

    @abstractmethod
    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> None:
        pass

    # 補上缺少的 Quiz 相關介面定義，讓 Repository 實作有所依據
    @abstractmethod
    def save_quiz_score(
        self, user_id: int, quiz_type: str, score: int, total_questions: int
    ) -> int:
        pass

    @abstractmethod
    def get_quiz_history(self, user_id: int) -> List[Dict[str, Any]]:
        pass


ISessionRepository = IDataRepository
