"""Vault: encrypt and decrypt .env secrets using Fernet symmetric encryption."""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

KEY_ENV_VAR = "ENVOY_VAULT_KEY"
DEFAULT_KEY_FILE = ".envoy.key"


def generate_key() -> bytes:
    """Generate a new Fernet key."""
    return Fernet.generate_key()


def load_key(key_file: str = DEFAULT_KEY_FILE) -> bytes:
    """Load key from env var or key file."""
    env_key = os.environ.get(KEY_ENV_VAR)
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key
    path = Path(key_file)
    if path.exists():
        return path.read_bytes().strip()
    raise FileNotFoundError(
        f"No vault key found. Set {KEY_ENV_VAR} or create {key_file}."
    )


def save_key(key: bytes, key_file: str = DEFAULT_KEY_FILE) -> None:
    """Persist key to a file."""
    Path(key_file).write_bytes(key)


def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a single string value, returning a base64 token string."""
    f = Fernet(key)
    token = f.encrypt(value.encode())
    return token.decode()


def decrypt_value(token: str, key: bytes) -> str:
    """Decrypt a token string back to plaintext."""
    f = Fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError(f"Decryption failed — invalid key or corrupted token.") from exc


def encrypt_env(env: dict, key: bytes, secrets_only: bool = True) -> dict:
    """Return a new dict with secret values encrypted."""
    from envoy.masking import is_secret
    return {
        k: encrypt_value(v, key) if (not secrets_only or is_secret(k)) else v
        for k, v in env.items()
    }


def decrypt_env(env: dict, key: bytes, secrets_only: bool = True) -> dict:
    """Return a new dict with secret values decrypted."""
    from envoy.masking import is_secret
    result = {}
    for k, v in env.items():
        if not secrets_only or is_secret(k):
            try:
                result[k] = decrypt_value(v, key)
            except ValueError:
                result[k] = v  # leave untouched if decryption fails
        else:
            result[k] = v
    return result
