from dataclasses import dataclass
from typing import Any

from .service import WellKnownService


@dataclass
class GetOpenIdConfigurationUseCase:
    well_known_service: WellKnownService

    def execute(self) -> dict[str, Any]:
        return self.well_known_service.get_openid_configuration()


@dataclass
class GetJWKsUseCase:
    well_known_service: WellKnownService

    def execute(self) -> dict[str, Any]:
        return self.well_known_service.get_jwks()
