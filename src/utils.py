import glob
import json
import os

from jwcrypto import jwk
from jwcrypto.common import json_decode

from src.config import settings
from src.logger import logger
from src.schemas import AppScopes, KeyPair


def load_certs() -> list[str]:
    certs = []
    try:
        for cert_path in glob.glob(os.path.join(settings.CERT_DIR, "*.pem")):
            with open(cert_path) as f:
                certs.append(f.read())

        if len(certs) == 0:
            raise Exception("No certs were found")
        return certs

    except Exception:
        logger.critical("Failed to load certs: ", exc_info=True)
        raise


def create_jwk_keys_from_certs(certs: list[str]) -> list[tuple[jwk.JWK, jwk.JWK]]:
    jwk_keys = []
    for cert in certs:
        private_key = jwk.JWK.from_pem(cert.encode())
        public_key = jwk.JWK()
        public_key.import_key(**json_decode(private_key.export_public()))
        jwk_keys.append((private_key, public_key))
    return jwk_keys


def load_certs_and_create_key_pairs() -> list[KeyPair]:
    certs = load_certs()
    jwk_keys = create_jwk_keys_from_certs(certs)
    return [KeyPair(private_key=private_key, public_key=public_key) for private_key, public_key in jwk_keys]


def load_app_scopes() -> AppScopes:
    try:
        with open(settings.AUTHORITATIVE_APPS_PATH) as f:
            d = json.loads(f.read())
            loaded_scopes = d["scopes"]
            d = {}
            app_scopes = AppScopes.model_validate(loaded_scopes)
            return app_scopes
    except Exception as e:
        logger.error("Failed to load authoritative apps: ", exc_info=False)
        raise e
