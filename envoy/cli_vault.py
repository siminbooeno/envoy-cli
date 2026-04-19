"""CLI commands for vault operations (encrypt / decrypt / keygen)."""

import sys
from pathlib import Path

from envoy.vault import generate_key, load_key, save_key, encrypt_env, decrypt_env
from envoy.parser import load_env_file, serialize_env


def cmd_keygen(key_file: str = ".envoy.key", force: bool = False) -> None:
    """Generate a new vault key and save it."""
    path = Path(key_file)
    if path.exists() and not force:
        print(f"Key file '{key_file}' already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)
    key = generate_key()
    save_key(key, key_file)
    print(f"New vault key written to {key_file}")


def cmd_encrypt(env_file: str, output_file: str | None = None, key_file: str = ".envoy.key", secrets_only: bool = True) -> None:
    """Encrypt secret values in an env file."""
    key = load_key(key_file)
    env = load_env_file(env_file)
    encrypted = encrypt_env(env, key, secrets_only=secrets_only)
    out = output_file or env_file
    Path(out).write_text(serialize_env(encrypted))
    print(f"Encrypted secrets written to {out}")


def cmd_decrypt(env_file: str, output_file: str | None = None, key_file: str = ".envoy.key", secrets_only: bool = True) -> None:
    """Decrypt secret values in an env file."""
    key = load_key(key_file)
    env = load_env_file(env_file)
    decrypted = decrypt_env(env, key, secrets_only=secrets_only)
    out = output_file or env_file
    Path(out).write_text(serialize_env(decrypted))
    print(f"Decrypted secrets written to {out}")
