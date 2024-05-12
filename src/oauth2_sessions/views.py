from fastapi import APIRouter
from pydantic import NonNegativeInt

from .dependencies import OAuth2SessionsServiceDep
from .schemas import OAuth2SessionCollection

router = APIRouter(prefix="", tags=["apps_sessions"])


@router.get("/")
async def get_oauth2_sessions(
    service: OAuth2SessionsServiceDep,
    count: NonNegativeInt = 20,
    offset: NonNegativeInt = 0,
) -> OAuth2SessionCollection:
    sessions = await service.get_many(count=count, offset=offset)
    return OAuth2SessionCollection(auth_apps=sessions)
