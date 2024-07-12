from pydantic import BaseModel


class LoginReq(BaseModel):
    login: str
    password: str


class RegistrationSchema(BaseModel):
    username: str
    email: str
    password: str
