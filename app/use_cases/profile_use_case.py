class ProfileUseCase:
    def __init__(self, chat_repo, quiz_repo):
        self.chat_repo = chat_repo
        self.quiz_repo = quiz_repo

    def get_user_profile_summary(self, user_id: int):
        chats = self.chat_repo.get_chat_history(user_id)
        quizzes = self.quiz_repo.get_quiz_history(user_id)

        total_quizzes = len(quizzes)
        avg_score = (
            sum(q.get("score", 0) for q in quizzes) / total_quizzes
            if total_quizzes > 0
            else 0
        )

        return {
            "chat_count": len(chats),
            "quiz_count": total_quizzes,
            "average_score": round(avg_score, 1),
            "quizzes": quizzes,
        }
