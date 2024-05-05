import bcrypt


def check(
    value: str,
    hashed_value: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=value.encode(),
        hashed_password=hashed_value,
    )


def create(value: str) -> bytes:
    return bcrypt.hashpw(
        password=value.encode(),
        salt=bcrypt.gensalt(),
    )
