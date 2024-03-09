from fastapi import FastAPI

from src.auth.sessions.views import router as sessions_router
from src.auth.views import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(sessions_router, prefix="/auth/sessions", tags=["sessions"])


@app.get("/ping")
def ping_pong() -> str:
    return "pong"
