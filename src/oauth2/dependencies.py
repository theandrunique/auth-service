from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic_auth = HTTPBasic(
    description="Basic authentication for the app. Use the format `client_id:client_secret`",
    auto_error=False,
)

AppAuth = Annotated[HTTPBasicCredentials, Depends(basic_auth)]
