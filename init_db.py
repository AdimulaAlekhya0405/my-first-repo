from database import engine, Base
import asyncio
from models import Order, User


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

asyncio.run(init_db())
