from dataclasses import asdict, dataclass, field
from enum import Enum

from fastapi import Request, status
from fastapi.responses import ORJSONResponse


class ServiceErrorCode(Enum):
    INVALID_FORM_BODY = 1
    USER_NOT_FOUND = 2
    INACTIVE_USER = 3
    INVALID_SESSION = 4
    APP_NOT_FOUND = 5
    INSUFFICIENT_PERMISSIONS = 6
    INVALID_CLIENT_ID = 7
    INVALID_CLIENT_CREDENTIALS = 8
    INVALID_CODE_VERIFIER = 9
    INVALID_AUTHORIZATION_CODE = 10
    NOT_MATCHING_CONFIGURATION = 11
    INVALID_REDIRECT_URI = 12
    INVALID_REFRESH_TOKEN = 13


SERVICE_ERROR_CODE_MESSAGES = {
    ServiceErrorCode.INVALID_FORM_BODY: "Invalid form body",
    ServiceErrorCode.USER_NOT_FOUND: "User was not found",
    ServiceErrorCode.INACTIVE_USER: "User was deleted",
    ServiceErrorCode.INVALID_SESSION: "Invalid session",
    ServiceErrorCode.APP_NOT_FOUND: "App was not found",
    ServiceErrorCode.INSUFFICIENT_PERMISSIONS: "Not enough permissions to perform this action",
    ServiceErrorCode.INVALID_CLIENT_ID: "Invalid client_id",
    ServiceErrorCode.INVALID_CLIENT_CREDENTIALS: "Invalid client credentials",
}


def get_service_error_code_message(error_code: ServiceErrorCode) -> str:
    try:
        return SERVICE_ERROR_CODE_MESSAGES[error_code]
    except KeyError:
        return error_code.name


class FieldErrorCode(Enum):
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    USERNAME_ALREADY_TAKEN = "USERNAME_ALREADY_TAKEN"
    INVALID_LOGIN = "INVALID_LOGIN"
    FIELD_REQUIRED = "FIELD_REQUIRED"


FIELD_ERROR_CODE_MESSAGES = {
    FieldErrorCode.EMAIL_ALREADY_REGISTERED: "Email already registered",
    FieldErrorCode.USERNAME_ALREADY_TAKEN: "Username already taken",
    FieldErrorCode.INVALID_LOGIN: "Login or password is invalid",
}


def get_field_error_code_message(error_code: FieldErrorCode) -> str:
    try:
        return FIELD_ERROR_CODE_MESSAGES[error_code]
    except KeyError:
        return error_code.name


@dataclass
class FieldError(Exception):
    code: FieldErrorCode
    message: str = field(init=False)

    def __post_init__(self):
        self.message = get_field_error_code_message(self.code)


@dataclass
class ServiceError(Exception):
    code: ServiceErrorCode
    message: str = field(init=False)
    errors: dict[str, FieldError] | None = None

    def __post_init__(self):
        self.message = get_service_error_code_message(self.code)


async def service_error_handler(request: Request, exc: ServiceError) -> ORJSONResponse:
    error_dict = asdict(exc)
    if not exc.errors:
        error_dict.pop("errors")

    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_dict,
    )
