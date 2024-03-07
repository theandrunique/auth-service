from fastapi import FastAPI

from src.auth.views import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/ping")
def ping_pong() -> str:
    return "pong"
