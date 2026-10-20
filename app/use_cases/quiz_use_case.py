# usecase/quiz_usecase.py
import random
from app.infrastructure.quiz import (
    QUESTIONS,
    LEVEL_CONFIG,
    QUESTIONS_PER_ROUND,
    PTS_PER_CORRECT,
)


class QuizUseCase:
    @staticmethod
    def start_quiz(level: str):
        pool = QUESTIONS.get(level, [])
        picked = random.sample(pool, min(len(pool), QUESTIONS_PER_ROUND))

        quiz_set = []
        for q, correct, wrongs in picked:
            options = [correct] + list(wrongs)
            random.shuffle(options)
            quiz_set.append(
                {
                    "question": q,
                    "correct": correct,
                    "options": options,
                }
            )

        return {
            "level": level,
            "level_label": LEVEL_CONFIG[level]["label"],
            "time_limit": LEVEL_CONFIG[level]["time"],
            "set": quiz_set,
        }

    @staticmethod
    def evaluate_answer(item_correct: str, item_options: list, chosen_option: str):
        correct_index = item_options.index(item_correct)
        chosen_index = (
            item_options.index(chosen_option) if chosen_option is not None else -1
        )
        isCorrect = chosen_index == correct_index

        earned_score = PTS_PER_CORRECT if isCorrect else 0
        return {
            "isCorrect": isCorrect,
            "correctIndex": correct_index,
            "earnedScore": earned_score,
        }

    @staticmethod
    def finalize_quiz(correct_count: int, total: int, elapsed_sec: int, score: float):
        accuracy = round((correct_count / total) * 100) if total > 0 else 0
        final_score = round(score)

        title = "挑戰完成！"
        sub = "繼續探索星海，成為真正的宇宙觀測者。"
        if accuracy == 100:
            title = "完美通關！"
            sub = "(👉ﾟヮﾟ)👉"
        elif accuracy >= 80:
            title = "表現優異！"
            sub = "(❁´◡`❁)"
        elif accuracy < 50:
            title = "挑戰完成"
            sub = "(o゜▽゜)o☆"

        return {
            "total": total,
            "accuracy": accuracy,
            "elapsedSec": elapsed_sec,
            "finalScore": final_score,
            "title": title,
            "sub": sub,
        }
