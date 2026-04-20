"""Tests for envoy/export.py and envoy/cli_export.py."""

import argparse
import json
import os
import pytest

from envoy.export import export_shell, export_json, export_docker, export_env
from envoy.cli_export import cmd_export


SAMPLE_ENV = {
    "APP_NAME": "envoy",
    "SECRET_KEY": "supersecret",
    "PORT": "8080",
}


def test_export_shell_contains_export():
    result = export_shell(SAMPLE_ENV)
    assert 'export APP_NAME="envoy"' in result
    assert 'export PORT="8080"' in result


def test_export_shell_masked_hides_secret():
    result = export_shell(SAMPLE_ENV, masked=True)
    assert "supersecret" not in result
    assert "SECRET_KEY" in result


def test_export_json_valid_json():
    result = export_json(SAMPLE_ENV)
    parsed = json.loads(result)
    assert parsed["APP_NAME"] == "envoy"
    assert parsed["PORT"] == "8080"


def test_export_json_masked_hides_secret():
    result = export_json(SAMPLE_ENV, masked=True)
    parsed = json.loads(result)
    assert "supersecret" not in parsed["SECRET_KEY"]


def test_export_docker_format():
    result = export_docker(SAMPLE_ENV)
    assert "APP_NAME=envoy" in result
    assert "PORT=8080" in result
    # No 'export' keyword
    assert "export" not in result


def test_export_env_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE_ENV, fmt="xml")


def test_export_env_writes_to_file(tmp_path):
    out = tmp_path / "out.sh"
    export_env(SAMPLE_ENV, fmt="shell", output_path=str(out))
    assert out.exists()
    content = out.read_text()
    assert 'export APP_NAME="envoy"' in content


def test_export_env_returns_string():
    result = export_env(SAMPLE_ENV, fmt="json")
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert "APP_NAME" in parsed


def test_cmd_export_stdout(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=envoy\nPORT=8080\n")

    args = argparse.Namespace(
        file=str(env_file),
        format="docker",
        masked=False,
        output=None,
    )
    cmd_export(args)
    captured = capsys.readouterr()
    assert "APP_NAME=envoy" in captured.out


def test_cmd_export_missing_file_exits(tmp_path):
    args = argparse.Namespace(
        file=str(tmp_path / "nonexistent.env"),
        format="shell",
        masked=False,
        output=None,
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_export(args)
    assert exc_info.value.code == 1
