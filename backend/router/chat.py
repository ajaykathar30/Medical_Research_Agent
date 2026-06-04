# app/routers/chats.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from database import get_db, SessionLocal
from models import Chat, User, Message
from schema import ChatCreate, ChatOut, ChatDetail, MessageCreate, MessageOut
from security import get_current_user
import json
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk

router = APIRouter(prefix="/chats", tags=["chats"])

# HELPER FUNCTION
def _chunk_text(chunk) -> str:
    content = chunk.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            p.get("text", "") for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        )
    return ""

@router.post("", response_model=ChatOut)
async def create_chat(
    body: ChatCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = Chat(user_id=user.id, title=body.title or "New chat")
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


@router.get("", response_model=list[ChatOut])
async def list_chats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(
        select(Chat).where(Chat.user_id == user.id).order_by(Chat.created_at.desc())
    )
    return list(result)


@router.get("/{chat_id}", response_model=ChatDetail)
async def get_chat(
    chat_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = await db.scalar(
        select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.messages))
    )
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    await db.delete(chat)
    await db.commit()
    return {"ok": True}




@router.post("/{chat_id}/messages", response_model=MessageOut)
async def send_message(
    chat_id: str,
    body: MessageCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 1. persist the user's message (and auto-title on the first one)
    db.add(Message(chat_id=chat_id, role="user", content=body.content))
    if chat.title in ("New chat", "New Chat"):
        chat.title = body.content[:50]
    await db.commit()

    # 2. run the agent on THIS chat's thread (chat_id == thread_id)
    agent = request.app.state.agent
    try:
        result = await agent.ainvoke(
            {"query": body.content},
            config={"configurable": {"thread_id": chat_id}},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    # 3. persist the assistant's answer
    assistant_msg = Message(chat_id=chat_id, role="assistant", content=result.get("answer", ""))
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)
    return assistant_msg


@router.post("/{chat_id}/messages/stream")
async def send_message_stream(
    chat_id: str,
    body: MessageCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    # save the user message up front (and auto-title)
    db.add(Message(chat_id=chat_id, role="user", content=body.content))
    if chat.title in ("New chat", "New Chat"):
        chat.title = body.content[:50]
    await db.commit()

    agent = request.app.state.agent

    async def event_generator():
        parts: list[str] = []
        try:
            async for chunk, metadata in agent.astream(
                {"query": body.content},
                config={"configurable": {"thread_id": chat_id}},
                stream_mode="messages",
            ):
                # only stream tokens from the answer node
                if metadata.get("langgraph_node") != "answer":
                    continue
                if not isinstance(chunk, AIMessageChunk):
                    continue
                text = _chunk_text(chunk)
                if text:
                    parts.append(text)
                    yield f"data: {json.dumps({'token': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # stream done → persist the full answer with a FRESH session
        answer = "".join(parts)
        async with SessionLocal() as s:
            s.add(Message(chat_id=chat_id, role="assistant", content=answer))
            await s.commit()

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
