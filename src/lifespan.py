from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.logger import logger
from src.mongo import test_connection
from src.redis_helper import redis_client


async def on_startup(app: FastAPI) -> None:
    await test_connection()
    logger.info("Redis connected: ", await redis_client.info())


async def on_shutdown(app: FastAPI) -> None: ...


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await on_startup(app)
    yield
    await on_shutdown(app)
