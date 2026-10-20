from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.use_cases.quiz_use_case import QuizUseCase
from app.infrastructure.database.repository import SQLiteRepository

router = APIRouter(prefix="/quiz", tags=["quiz"])
_db_repo = SQLiteRepository()


class AnswerCheckRequest(BaseModel):
    correct_answer: str
    options: List[str]
    chosen_option: Optional[str] = None


class FinishRequest(BaseModel):
    user_id: int = 1
    level: str
    correct_count: int
    total: int
    elapsed_sec: int
    score: float


@router.get("/start/{level}")
def api_start_quiz(level: str):
    return QuizUseCase.start_quiz(level)


@router.post("/check")
def api_check_answer(data: AnswerCheckRequest):
    return QuizUseCase.evaluate_answer(
        data.correct_answer, data.options, data.chosen_option
    )


@router.post("/finish")
def api_finish_quiz(data: FinishRequest):
    summary = QuizUseCase.finalize_quiz(
        data.correct_count, data.total, data.elapsed_sec, data.score
    )

    try:
        quiz_type = f"Level {data.level}"
        _db_repo.save_quiz_score(
            user_id=data.user_id,
            quiz_type=quiz_type,
            score=int(data.score),
            total_questions=data.total,
        )
    except Exception as e:
        print(f"❌ [DB] 自動儲存測驗成績失敗: {e}")

    return summary


@router.get("/history/{user_id}")
def get_quiz_history(user_id: int):
    return _db_repo.get_quiz_history(user_id)


@router.delete("/history/{user_id}")
def clear_quiz_history(user_id: int):
    _db_repo.clear_quiz_history(user_id)
    return {"status": "success"}


@router.delete("/score/{score_id}")
def delete_quiz_score(score_id: int, user_id: int = 1):
    success = _db_repo.delete_quiz_score(score_id, user_id)
    return {"status": "success", "deleted": success}
