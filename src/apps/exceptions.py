from fastapi import HTTPException, status


class AppNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found",
        )


class UnauthorizedAccess(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="You do not have permission to this application"
        )
