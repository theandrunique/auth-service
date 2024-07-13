class PasswordValidationError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Password should have at least 8 characters, "
            "contain at least one uppercase letter, one lowercase letter, "
            "one number and one special character from #?!@$%^&*-",
        )


class UsernameValidationError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Username should have at least 3 characters, "
            "can only contain letters, numbers and underscores",
        )
