from typing import Any

from fastapi import APIRouter

from src.dependencies import Provide
from src.well_known.service import WellKnownService

router = APIRouter(prefix="/.well-known", tags=["well-known"])


@router.get("/openid-configuration")
def openid_configuration(
    well_known_service=Provide(WellKnownService),
) -> dict[str, Any]:
    return well_known_service.get_openid_configuration()


@router.get("/jwks.json")
def jwks_endpoint(
    well_known_service=Provide(WellKnownService),
) -> dict[str, Any]:
    return well_known_service.get_jwks()
