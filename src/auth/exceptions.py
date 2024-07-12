from fastapi import HTTPException, status

from src.exceptions import FieldError, FieldErrorCode, ServiceError, ServiceErrorCode


class NotAuthenticated(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


class InvalidCredentials(ServiceError):
    def __init__(self) -> None:
        super().__init__(
            code=ServiceErrorCode.INVALID_FORM_BODY,
            errors={
                "login": FieldError(code=FieldErrorCode.INVALID_LOGIN),
                "password": FieldError(code=FieldErrorCode.INVALID_LOGIN),
            },
        )


class InvalidSession(ServiceError):
    def __init__(self) -> None:
        super().__init__(
            code=ServiceErrorCode.INVALID_SESSION,
        )
