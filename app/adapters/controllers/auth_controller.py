from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.infrastructure.database.database import (
    create_user,
    get_user_by_username,
    verify_password,
    get_conn
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserAuthRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class GuestLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)


@router.post("/register", summary="使用者註冊")
def register_user(data: UserAuthRequest):
    existing_user = get_user_by_username(data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此使用者名稱已被註冊，請選擇其他名稱。"
        )
    try:
        user_id = create_user(username=data.username,
                              password=data.password, role_type="registered")
        return {
            "status": "success",
            "message": "註冊成功",
            "user_id": user_id,
            "username": data.username,
            "role_type": "registered"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"註冊失敗: {str(e)}"
        )


@router.post("/login", summary="一般帳號登入")
def login_user(data: UserAuthRequest):
    user = verify_password(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼錯誤。"
        )
    return {
        "status": "success",
        "message": "登入成功",
        "user_id": user["user_id"],
        "username": user["username"],
        "role_type": user["role_type"]
    }


@router.post("/guest", summary="訪客身分登入")
def guest_login(data: GuestLoginRequest):
    user = get_user_by_username(data.username)
    if user:
        return {
            "status": "success",
            "message": "訪客登入成功",
            "user_id": user["user_id"],
            "username": user["username"],
            "role_type": user["role_type"]
        }
    try:
        user_id = create_user(username=data.username,
                              password=None, role_type="guest")
        return {
            "status": "success",
            "message": "訪客帳號建立並登入成功",
            "user_id": user_id,
            "username": data.username,
            "role_type": "guest"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"訪客登入初始化失敗: {str(e)}"
        )


@router.get("/profile/{user_id}", summary="取得使用者個人檔案與相關紀錄")
def get_user_profile(user_id: int):
    """
    根據 user_id 查詢對應的使用者基本資料、測驗歷史與互動紀錄，確保多使用者資料完全隔離。
    """
    with get_conn() as conn:
        user = conn.execute(
            "SELECT user_id, username, role_type, created_at FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="找不到此使用者")

        quizzes = conn.execute(
            "SELECT * FROM quiz_scores WHERE user_id = ? ORDER BY completed_at DESC",
            (user_id,)
        ).fetchall()

        interactions = conn.execute(
            "SELECT * FROM interactions WHERE user_id = ? ORDER BY ts DESC LIMIT 20",
            (user_id,)
        ).fetchall()

        return {
            "user": dict(user),
            "quiz_history": [dict(q) for q in quizzes],
            "interactions": [dict(i) for i in interactions]
        }
