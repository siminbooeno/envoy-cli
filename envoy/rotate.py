"""Key rotation support: re-encrypt env values with a new vault key."""

from pathlib import Path
from typing import Dict, List, Tuple

from envoy.vault import encrypt_value, decrypt_value, load_key
from envoy.masking import is_secret
from envoy.parser import load_env_file, serialize_env


def rotate_secrets(
    env: Dict[str, str],
    old_key: bytes,
    new_key: bytes,
) -> Tuple[Dict[str, str], List[str]]:
    """Re-encrypt all secret values using a new key.

    Returns the updated env dict and a list of rotated key names.
    """
    rotated: List[str] = []
    updated = dict(env)

    for k, v in env.items():
        if not is_secret(k):
            continue
        try:
            plaintext = decrypt_value(v, old_key)
            updated[k] = encrypt_value(plaintext, new_key)
            rotated.append(k)
        except Exception:
            # Value was not encrypted — skip silently
            pass

    return updated, rotated


def rotate_env_file(
    env_path: Path,
    old_key_path: Path,
    new_key_path: Path,
) -> List[str]:
    """Load an env file, rotate its secrets in-place, return rotated keys."""
    env = load_env_file(env_path)
    old_key = load_key(old_key_path)
    new_key = load_key(new_key_path)

    updated, rotated = rotate_secrets(env, old_key, new_key)

    if rotated:
        env_path.write_text(serialize_env(updated))

    return rotated
