from fastapi import HTTPException, status


class PasswordValidationError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Password should have at least 8 characters, "
            "contain at least one uppercase letter, one lowercase letter, "
            "one number and one special character from #?!@$%^&*-",
        )


class UserNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class InactiveUser(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )


class InvalidImageUrl(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid image URL")
