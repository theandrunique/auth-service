from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClientSession

from .client import client


async def mongo_session() -> AsyncGenerator[AsyncIOMotorClientSession, None]:
    session = await client.start_session()
    yield session
    await session.end_session()


MongoSession = Annotated[AsyncIOMotorClientSession, Depends(mongo_session)]
