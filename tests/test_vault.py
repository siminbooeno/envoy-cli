"""Tests for envoy.vault encryption/decryption."""

import pytest
from envoy.vault import (
    generate_key,
    encrypt_value,
    decrypt_value,
    encrypt_env,
    decrypt_env,
    save_key,
    load_key,
)


@pytest.fixture
def key():
    return generate_key()


def test_generate_key_returns_bytes(key):
    assert isinstance(key, bytes)
    assert len(key) > 0


def test_encrypt_decrypt_roundtrip(key):
    original = "super_secret_value"
    token = encrypt_value(original, key)
    assert token != original
    assert decrypt_value(token, key) == original


def test_decrypt_wrong_key_raises(key):
    token = encrypt_value("secret", key)
    wrong_key = generate_key()
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_value(token, wrong_key)


def test_encrypt_env_only_secrets(key):
    env = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp", "API_SECRET": "abc123"}
    encrypted = encrypt_env(env, key, secrets_only=True)
    assert encrypted["APP_NAME"] == "myapp"  # non-secret unchanged
    assert encrypted["DB_PASSWORD"] != "hunter2"
    assert encrypted["API_SECRET"] != "abc123"


def test_encrypt_env_all_values(key):
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    encrypted = encrypt_env(env, key, secrets_only=False)
    assert encrypted["APP_NAME"] != "myapp"
    assert encrypted["PORT"] != "8080"


def test_decrypt_env_roundtrip(key):
    env = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    encrypted = encrypt_env(env, key, secrets_only=True)
    decrypted = decrypt_env(encrypted, key, secrets_only=True)
    assert decrypted == env


def test_save_and_load_key(tmp_path, key):
    key_file = str(tmp_path / ".envoy.key")
    save_key(key, key_file)
    loaded = load_key(key_file)
    assert loaded == key


def test_load_key_from_env_var(monkeypatch, key):
    monkeypatch.setenv("ENVOY_VAULT_KEY", key.decode())
    loaded = load_key()
    assert loaded == key


def test_load_key_missing_raises(tmp_path):
    key_file = str(tmp_path / "nonexistent.key")
    with pytest.raises(FileNotFoundError):
        load_key(key_file)
