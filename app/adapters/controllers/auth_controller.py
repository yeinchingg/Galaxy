from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from app.infrastructure.database.repository import (
    create_user,
    get_user_by_username,
    verify_password,
)
from datetime import datetime, timedelta, timezone
router = APIRouter(prefix="/auth", tags=["Authentication"])

load_dotenv()  

SECRET_KEY = os.getenv("JWT_SECRET", "your_fallback_secret_key")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token_header(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="未提供有效授權憑證 (Missing Token)")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已過期，請重新登入")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無效的 Token")


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
            status_code=status.HTTP_409_CONFLICT,
            detail="這個使用者名稱已經被註冊了",
        )
    try:
        user_id = create_user(
            username=data.username, password=data.password, role_type="member"
        )
        # 註冊成功後順便產生 Token
        token = create_access_token(
            {"user_id": user_id, "username": data.username})
        return {
            "status": "success",
            "message": "註冊成功",
            "user_id": user_id,
            "username": data.username,
            "role": "member",
            "token": token,  # <--- 加上 token
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"註冊失敗: {str(e)}",
        )


@router.post("/login", summary="一般帳號登入")
def login_user(data: UserAuthRequest):
    user = verify_password(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤。"
        )
    # 登入成功產生 Token
    token = create_access_token(
        {"user_id": user["user_id"], "username": user["username"]})
    return {
        "status": "success",
        "message": "登入成功",
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role_type"],
        "token": token,  # <--- 加上 token
    }


@router.post("/guest", summary="訪客身分登入")
def guest_login(data: GuestLoginRequest):
    user = get_user_by_username(data.username)
    if user:
        token = create_access_token(
            {"user_id": user["user_id"], "username": user["username"]})
        return {
            "status": "success",
            "message": "訪客登入成功",
            "user_id": user["user_id"],
            "username": user["username"],
            "role": "guest",
            "token": token,
        }
    try:
        user_id = create_user(username=data.username,
                              password=None, role_type="guest")
        token = create_access_token(
            {"user_id": user_id, "username": data.username})
        return {
            "status": "success",
            "message": "訪客帳號建立並登入成功",
            "user_id": user_id,
            "username": data.username,
            "role": "guest",
            "token": token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"訪客登入初始化失敗: {str(e)}",
        )
