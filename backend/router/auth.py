# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schema import UserCreate, UserLogin, UserOut
from security import hash_password, verify_password, create_access_token, get_current_user
from config import COOKIE_NAME, COOKIE_SECURE, COOKIE_SAMESITE, ACCESS_TOKEN_EXPIRE

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,                 # JS can't read it
        secure=COOKIE_SECURE,          # only over HTTPS in prod
        samesite=COOKIE_SAMESITE,
        max_age=int(ACCESS_TOKEN_EXPIRE.total_seconds()),
        path="/",
    )


@router.post("/register", response_model=UserOut)
async def register(body: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    _set_auth_cookie(response, create_access_token(user.id))
    return user


@router.post("/login", response_model=UserOut)
async def login(body: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    _set_auth_cookie(response, create_access_token(user.id))
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user