from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI


async def on_startup(app: FastAPI) -> None: ...


async def on_shutdown(app: FastAPI) -> None: ...


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup(app)
    yield
    await on_shutdown(app)
