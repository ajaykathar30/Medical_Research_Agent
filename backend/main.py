# main.py
import sys
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from psycopg import AsyncConnection                          
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from router import auth, chat

from config import CHECKPOINTER_DB_URI, CORS_ORIGINS

from ai.graph import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):

    conn = await AsyncConnection.connect(                     
        CHECKPOINTER_DB_URI,
        autocommit=True,
        prepare_threshold=None,
    )
    try:
        checkpointer = AsyncPostgresSaver(conn)
        await checkpointer.setup()                           
        app.state.agent = build_graph(checkpointer=checkpointer)
        yield
    finally:
        await conn.close()                                   


app = FastAPI(title="Medical Research Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)