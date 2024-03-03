import uvicorn
from auth.views import router as auth_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router, prefix="")


@app.get("/ping")
def ping_pong() -> str:
    return "pong"


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
