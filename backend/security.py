# app/security.py
import bcrypt
import jwt
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE, COOKIE_NAME


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE}
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = request.cookies.get(COOKIE_NAME)          # <-- read JWT from the cookie
    if not token:
        raise cred_exc
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise cred_exc
    user = await db.get(User, user_id)
    if user is None:
        raise cred_exc
    return user