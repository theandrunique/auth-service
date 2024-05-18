from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.apps.views import router as apps_router
from src.auth.views import router as auth_router
from src.config import settings
from src.lifespan import lifespan
from src.oauth2.views import router as oauth2_router
from src.sessions.views import router as sessions_router
from src.users.views import router as users_router
from src.well_known.views import router as well_known

origins = [
    settings.FRONTEND_URL,
]

app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(apps_router, prefix="/apps", tags=["apps"])
app.include_router(oauth2_router, prefix="/oauth", tags=["oauth2"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
app.include_router(well_known)

if settings.EMAILS_ENABLED:
    from src.emails.views import router as emails_router

    app.include_router(emails_router, prefix="/emails", tags=["emails"])


SESSION_COOKIE_KEY = "session_id"


@app.get("/ping", tags=["healthcheck"])
def ping_pong() -> dict[str, str]:
    return {"ping": "pong"}
