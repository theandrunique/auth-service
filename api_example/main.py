from fastapi import FastAPI

from auth import auth_router

import uvicorn


app = FastAPI()

app.include_router(auth_router, prefix="")

@app.get("/ping")
def ping_pong():
    return "pong"

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")