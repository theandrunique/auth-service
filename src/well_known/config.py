from jwcrypto import jwk

from src.config import settings

key = jwk.JWK.from_pem(settings.PRIVATE_KEY.encode())
public_key_pem = key.export_to_pem()
