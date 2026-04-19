"""Integration tests for CLI vault commands."""

import pytest
from pathlib import Path
from envoy.vault import generate_key, save_key, decrypt_value, load_key
from envoy.cli_vault import cmd_keygen, cmd_encrypt, cmd_decrypt
from envoy.parser import load_env_file


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP_NAME=myapp\nDB_PASSWORD=secret123\nAPI_KEY=xyz\n")
    return str(p)


@pytest.fixture
def key_file(tmp_path):
    key = generate_key()
    kf = str(tmp_path / ".envoy.key")
    save_key(key, kf)
    return kf


def test_cmd_keygen_creates_file(tmp_path):
    kf = str(tmp_path / ".envoy.key")
    cmd_keygen(key_file=kf)
    assert Path(kf).exists()
    assert len(Path(kf).read_bytes()) > 0


def test_cmd_keygen_no_overwrite(tmp_path):
    kf = str(tmp_path / ".envoy.key")
    cmd_keygen(key_file=kf)
    with pytest.raises(SystemExit):
        cmd_keygen(key_file=kf, force=False)


def test_cmd_keygen_force_overwrite(tmp_path):
    kf = str(tmp_path / ".envoy.key")
    cmd_keygen(key_file=kf)
    cmd_keygen(key_file=kf, force=True)  # should not raise


def test_cmd_encrypt_modifies_secrets(env_file, key_file):
    cmd_encrypt(env_file, key_file=key_file)
    env = load_env_file(env_file)
    assert env["APP_NAME"] == "myapp"  # unchanged
    assert env["DB_PASSWORD"] != "secret123"  # encrypted


def test_cmd_encrypt_decrypt_roundtrip(env_file, key_file):
    original = load_env_file(env_file).copy()
    cmd_encrypt(env_file, key_file=key_file)
    cmd_decrypt(env_file, key_file=key_file)
    restored = load_env_file(env_file)
    assert restored["DB_PASSWORD"] == original["DB_PASSWORD"]
    assert restored["APP_NAME"] == original["APP_NAME"]


def test_cmd_encrypt_to_output_file(env_file, key_file, tmp_path):
    out = str(tmp_path / ".env.encrypted")
    cmd_encrypt(env_file, output_file=out, key_file=key_file)
    assert Path(out).exists()
    enc_env = load_env_file(out)
    assert enc_env["DB_PASSWORD"] != "secret123"
    # original unchanged
    orig_env = load_env_file(env_file)
    assert orig_env["DB_PASSWORD"] == "secret123"
