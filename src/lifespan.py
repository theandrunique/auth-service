from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.mongo import mongodb_info, ping_mongo
from src.redis import ping_redis


async def on_startup(app: FastAPI) -> None:
    await ping_mongo()
    await mongodb_info()
    await ping_redis()


async def on_shutdown(app: FastAPI) -> None: ...


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    await on_startup(app)
    yield
    await on_shutdown(app)
