from src.exceptions import ServiceError, ServiceErrorCode


class AppNotFound(ServiceError):
    def __init__(self) -> None:
        super().__init__(code=ServiceErrorCode.APP_NOT_FOUND)
