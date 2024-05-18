from jwcrypto import jwk
from jwcrypto.common import json_decode

from src.config import settings

private_key = jwk.JWK.from_pem(settings.PRIVATE_KEY.encode())
public_key_pem = private_key.export_to_pem()

public_key = jwk.JWK()
public_key.import_key(**json_decode(private_key.export_public()))
