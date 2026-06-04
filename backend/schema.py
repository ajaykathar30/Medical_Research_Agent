# app/schemas.py
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr

    model_config = {"from_attributes": True}



from datetime import datetime


class ChatCreate(BaseModel):
    title: str | None = None


class ChatOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ChatDetail(ChatOut):
    messages: list[MessageOut]


class MessageCreate(BaseModel):
    content: str