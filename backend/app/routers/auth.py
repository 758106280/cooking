from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import LoginRequest, ProfileUpdate, RegisterRequest, UserOut


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    request.session["user_id"] = user.id
    data = UserOut.model_validate(user).model_dump()
    data["access_token"] = create_access_token(user.id)
    return {"data": data, "message": "登录成功"}


@router.post("/register")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(
        username=payload.username,
        nickname=payload.nickname or payload.username,
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    data = UserOut.model_validate(user).model_dump()
    data["access_token"] = create_access_token(user.id)
    return {"data": data, "message": "注册成功"}


@router.post("/logout")
def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"message": "已退出登录"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"data": UserOut.model_validate(user), "message": "success"}


@router.put("/profile")
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatar is not None:
        user.avatar = payload.avatar
    db.commit()
    db.refresh(user)
    return {"data": UserOut.model_validate(user), "message": "资料已保存"}
