from fastapi import HTTPException, status


class UsernameOrEmailAlreadyExists(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )


class InvalidCredentials(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username or password",
        )


class InvalidToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


class EmailNotVerified(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not verified",
        )


class EmailAlreadyVerified(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
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


class NotAuthenticated(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PasswordValidationError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Password should have at least 8 characters, "
            "contain at least one uppercase letter, one lowercase letter, "
            "one number and one special character from #?!@$%^&*-",
        )


class NotSupportedByOAuth2(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Endpoint is not supported by OAuth2",
        )


class MissingScope(HTTPException):
    def __init__(self, scopes: list[str]) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scopes: '{', '.join(scopes)}' not allowed by the app",
        )
