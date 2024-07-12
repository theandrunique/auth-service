from src.exceptions import ServiceError, ServiceErrorCode


class InvalidClientId(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_CLIENT_ID)


class InvalidRefreshToken(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_REFRESH_TOKEN)


class NotMatchingConfiguration(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.NOT_MATCHING_CONFIGURATION)


class InvalidAuthorizationCode(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_AUTHORIZATION_CODE)


class InvalidClientCredentials(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_CLIENT_CREDENTIALS)


class InvalidCodeVerifier(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_CODE_VERIFIER)


class InvalidRedirectUri(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.INVALID_REDIRECT_URI)
