import random

from src.schemas import KeyPair


class KeyManager:
    def __init__(self, key_pairs: list[KeyPair]):
        self.key_pairs = key_pairs
        self.public_keys_by_kid = {key.private_key.thumbprint(): key.public_key for key in key_pairs}
        self.private_keys_by_kid = {key.private_key.thumbprint(): key.private_key for key in key_pairs}

    def get_random_key_pair(self) -> KeyPair:
        return random.choice(self.key_pairs)
