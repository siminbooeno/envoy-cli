"""Tests for envoy.rotate — key rotation logic."""

import pytest
from pathlib import Path

from envoy.vault import generate_key, encrypt_value, decrypt_value, save_key
from envoy.rotate import rotate_secrets, rotate_env_file
from envoy.parser import serialize_env, load_env_file


@pytest.fixture
def old_key() -> bytes:
    return generate_key()


@pytest.fixture
def new_key() -> bytes:
    return generate_key()


def test_rotate_secrets_re_encrypts_secret_keys(old_key, new_key):
    plaintext = "s3cr3t"
    env = {
        "API_KEY": encrypt_value(plaintext, old_key),
        "DEBUG": "true",
    }
    updated, rotated = rotate_secrets(env, old_key, new_key)

    assert "API_KEY" in rotated
    assert "DEBUG" not in rotated
    assert decrypt_value(updated["API_KEY"], new_key) == plaintext


def test_rotate_secrets_non_secret_keys_unchanged(old_key, new_key):
    env = {"HOST": "localhost", "PORT": "5432"}
    updated, rotated = rotate_secrets(env, old_key, new_key)

    assert rotated == []
    assert updated == env


def test_rotate_secrets_skips_unencrypted_secret_values(old_key, new_key):
    env = {"SECRET_KEY": "not-encrypted-value"}
    updated, rotated = rotate_secrets(env, old_key, new_key)

    assert rotated == []
    assert updated["SECRET_KEY"] == "not-encrypted-value"


def test_rotate_env_file_updates_file_on_disk(tmp_path, old_key, new_key):
    plaintext = "mysecret"
    env = {
        "DB_PASSWORD": encrypt_value(plaintext, old_key),
        "APP_NAME": "envoy",
    }
    env_file = tmp_path / ".env"
    env_file.write_text(serialize_env(env))

    old_key_path = tmp_path / "old.key"
    new_key_path = tmp_path / "new.key"
    save_key(old_key, old_key_path)
    save_key(new_key, new_key_path)

    rotated = rotate_env_file(env_file, old_key_path, new_key_path)

    assert "DB_PASSWORD" in rotated
    reloaded = load_env_file(env_file)
    assert decrypt_value(reloaded["DB_PASSWORD"], new_key) == plaintext
    assert reloaded["APP_NAME"] == "envoy"


def test_rotate_env_file_returns_empty_when_no_secrets(tmp_path, old_key, new_key):
    env = {"HOST": "localhost"}
    env_file = tmp_path / ".env"
    env_file.write_text(serialize_env(env))

    old_key_path = tmp_path / "old.key"
    new_key_path = tmp_path / "new.key"
    save_key(old_key, old_key_path)
    save_key(new_key, new_key_path)

    rotated = rotate_env_file(env_file, old_key_path, new_key_path)
    assert rotated == []
