import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.apps.views import router as apps_router
from src.auth.views import router as auth_router
from src.database import db_helper
from src.mongo_helper import mongo_client
from src.oauth2.models import OAuth2SessionsInDB
from src.oauth2.views import router as oauth2_router
from src.redis_helper import redis_client
from src.sessions.models import UserSessionsInDB
from src.sessions.views import router as sessions_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(OAuth2SessionsInDB.metadata.create_all)
        await conn.run_sync(UserSessionsInDB.metadata.create_all)
    logger.info("MongoDB connected: ", await mongo_client.server_info())
    logger.info("Redis connected: ", await redis_client.info())
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(sessions_router, prefix="/auth/sessions", tags=["sessions"])
app.include_router(apps_router, prefix="/apps", tags=["apps"])
app.include_router(oauth2_router, prefix="/oauth2", tags=["oauth2"])


@app.get("/ping")
def ping_pong() -> str:
    return "pong"
