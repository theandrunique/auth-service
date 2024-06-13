from fastapi import APIRouter
from pydantic import NonNegativeInt

from src.dependencies import Container, Provide

from .schemas import OAuth2SessionCollection

router = APIRouter()


@router.get("/")
async def get_oauth2_sessions(
    count: NonNegativeInt = 20,
    offset: NonNegativeInt = 0,
    service=Provide(Container.OAuth2SessionsService),
) -> OAuth2SessionCollection:
    sessions = await service.get_many(count=count, offset=offset)
    return OAuth2SessionCollection(auth_apps=sessions)
