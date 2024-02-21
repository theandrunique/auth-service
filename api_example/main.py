from fastapi import FastAPI

from auth import auth_router


app = FastAPI()

app.include_router(auth_router, prefix="")

@app.get("/ping")
def ping_pong():
    return "pong"