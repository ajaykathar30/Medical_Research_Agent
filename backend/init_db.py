# app/init_db.py
import asyncio
from database import engine, Base
import models  # noqa: F401  (registers the tables on Base)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("tables created")


asyncio.run(main())