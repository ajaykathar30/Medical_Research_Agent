# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")   # postgresql+psycopg://...  (async-capable)


engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # tests the connection before using it; reconnects if dead
    pool_recycle=300,        # recycle connections older than 5 min
    pool_size=5,
    max_overflow=10,
)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with SessionLocal() as session:
        yield session