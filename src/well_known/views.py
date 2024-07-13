from typing import Any

from fastapi import APIRouter

from src.dependencies import Provide

from .schemas import JWKSetSchema, OpenIdConfigurationSchema
from .use_cases import GetJWKsUseCase, GetOpenIdConfigurationUseCase

router = APIRouter(prefix="/.well-known", tags=["well-known"])


@router.get("/openid-configuration", response_model=OpenIdConfigurationSchema)
def openid_configuration(
    use_case=Provide(GetOpenIdConfigurationUseCase),
) -> Any:
    return use_case.execute()


@router.get("/jwks.json", response_model=JWKSetSchema)
def jwks_endpoint(
    use_case=Provide(GetJWKsUseCase),
) -> Any:
    return use_case.execute()
