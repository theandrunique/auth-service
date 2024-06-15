from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.utils import init_mongo_repositories


async def on_startup(app: FastAPI) -> None:
    await init_mongo_repositories()


async def on_shutdown(app: FastAPI) -> None: ...


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup(app)
    yield
    await on_shutdown(app)
