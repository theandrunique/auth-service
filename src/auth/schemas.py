from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class UserTokenSchema(BaseModel):
    user_id: int
    token: str


class UserTokenPayload(BaseModel):
    user_id: int
    email: str
    jti: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool


class RegistrationSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(
        min_length=3,
    )


class OtpAuthSchema(BaseModel):
    email: EmailStr
    otp: str


class OtpRequestSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(BaseModel):
    login: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    password: str = Field(
        min_length=3,
    )


class VerifyEmailSchema(BaseModel):
    token: str

