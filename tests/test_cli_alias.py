"""Tests for envoy.cli_alias module."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envoy.alias import add_alias, load_aliases
from envoy.cli_alias import cmd_alias


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASSWORD=secret\n")
    return f


def make_args(file: str, alias_action: str, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(file=file, alias_action=alias_action, **kwargs)


def test_cmd_alias_add_prints_confirmation(env_file, capsys):
    args = make_args(str(env_file), "add", alias="HOST", original="DB_HOST")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "HOST" in out
    assert "DB_HOST" in out


def test_cmd_alias_add_persists(env_file):
    args = make_args(str(env_file), "add", alias="HOST", original="DB_HOST")
    cmd_alias(args)
    aliases = load_aliases(env_file)
    assert aliases.get("HOST") == "DB_HOST"


def test_cmd_alias_remove_prints_confirmation(env_file, capsys):
    add_alias(env_file, "HOST", "DB_HOST")
    args = make_args(str(env_file), "remove", alias="HOST")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "HOST" in out
    assert load_aliases(env_file) == {}


def test_cmd_alias_remove_missing_prints_not_found(env_file, capsys):
    args = make_args(str(env_file), "remove", alias="GHOST")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_alias_resolve_prints_original(env_file, capsys):
    add_alias(env_file, "HOST", "DB_HOST")
    args = make_args(str(env_file), "resolve", alias="HOST")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_cmd_alias_resolve_missing_prints_not_found(env_file, capsys):
    args = make_args(str(env_file), "resolve", alias="NOWHERE")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_alias_list_shows_entries(env_file, capsys):
    add_alias(env_file, "HOST", "DB_HOST")
    add_alias(env_file, "PASS", "DB_PASSWORD")
    args = make_args(str(env_file), "list")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "HOST" in out
    assert "PASS" in out


def test_cmd_alias_list_empty_prints_message(env_file, capsys):
    args = make_args(str(env_file), "list")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_missing_file_prints_error(tmp_path, capsys):
    missing = tmp_path / "ghost.env"
    args = make_args(str(missing), "list")
    cmd_alias(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()
