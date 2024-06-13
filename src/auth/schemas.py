from pydantic import BaseModel


class LoginReq(BaseModel):
    login: str
    password: str
