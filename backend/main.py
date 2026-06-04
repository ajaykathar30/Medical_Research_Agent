# app/main.py
import sys
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver



from router import auth, chat

from config import CHECKPOINTER_DB_URI

from ai.graph import build_graph



@asynccontextmanager
async def lifespan(app: FastAPI):
    # one checkpointer + one compiled graph for the whole app lifetime
    async with AsyncPostgresSaver.from_conn_string(CHECKPOINTER_DB_URI) as checkpointer:
        await checkpointer.setup()                 # creates its tables (idempotent)
        app.state.agent = build_graph(checkpointer=checkpointer)
        yield
    # connection closes on shutdown


app = FastAPI(title="Medical Research Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)