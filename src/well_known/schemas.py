from pydantic import BaseModel


class OpenIdConfigurationSchema(BaseModel):
    authorization_endpoint: str
    token_endpoint: str
    issuer: str
    jwks_uri: str
    response_types_supported: list[str]
    grant_types_supported: list[str]
    id_token_signing_alg_values_supported: list[str]


class JWKSchema(BaseModel):
    kty: str
    alg: str
    use: str
    kid: str
    n: str
    e: str


class JWKSetSchema(BaseModel):
    keys: list[JWKSchema]
