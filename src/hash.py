import bcrypt


def check(value: str | bytes, hashed_value: bytes) -> bool:
    if isinstance(value, str):
        value = value.encode()
    elif not isinstance(value, bytes):
        raise ValueError("Value must be either str or bytes.")
    return bcrypt.checkpw(password=value, hashed_password=hashed_value)


def create(value: str | bytes) -> bytes:
    if isinstance(value, str):
        value = value.encode()
    elif not isinstance(value, bytes):
        raise ValueError("Value must be either str or bytes.")
    return bcrypt.hashpw(password=value, salt=bcrypt.gensalt())
