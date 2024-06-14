from fastapi import HTTPException, status


class RedirectUriNotAllowed(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redirect URI not allowed",
        )


class NotAllowedScope(HTTPException):
    def __init__(self, scopes: list[str]) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scopes: '{', '.join(scopes)}' not allowed by the app",
        )


class InvalidAuthorizationCode(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code",
        )


class InvalidAppCredentials(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid app credentials",
        )


class InvalidClientId(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client id",
        )


class InvalidCodeVerifier(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code verifier",
        )


class InvalidRequest(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {detail}",
        )
