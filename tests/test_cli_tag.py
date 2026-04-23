"""Tests for envoy/cli_tag.py"""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envoy.cli_tag import cmd_tag, build_tag_subparser
from envoy.tag import load_tags, add_tag


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nDEBUG=true\n")
    return f


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"file": "", "tag_action": "list", "key": None, "tag": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_tag_add_prints_confirmation(env_file: Path, capsys) -> None:
    args = make_args(file=str(env_file), tag_action="add", key="API_KEY", tag="secret")
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "Added" in out
    assert "secret" in out
    assert "API_KEY" in out


def test_cmd_tag_add_persists(env_file: Path, capsys) -> None:
    args = make_args(file=str(env_file), tag_action="add", key="API_KEY", tag="secret")
    cmd_tag(args)
    tags = load_tags(env_file)
    assert "secret" in tags.get("API_KEY", [])


def test_cmd_tag_remove_prints_confirmation(env_file: Path, capsys) -> None:
    add_tag(env_file, "API_KEY", "secret")
    args = make_args(file=str(env_file), tag_action="remove", key="API_KEY", tag="secret")
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_tag_list_all_tags(env_file: Path, capsys) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "DEBUG", "optional")
    args = make_args(file=str(env_file), tag_action="list", key=None)
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "secret" in out
    assert "optional" in out


def test_cmd_tag_list_specific_key(env_file: Path, capsys) -> None:
    add_tag(env_file, "API_KEY", "secret")
    args = make_args(file=str(env_file), tag_action="list", key="API_KEY")
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "secret" in out


def test_cmd_tag_list_no_tags(env_file: Path, capsys) -> None:
    args = make_args(file=str(env_file), tag_action="list", key=None)
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_filter_returns_keys(env_file: Path, capsys) -> None:
    add_tag(env_file, "API_KEY", "secret")
    add_tag(env_file, "DB_PASS", "secret")
    args = make_args(file=str(env_file), tag_action="filter", tag="secret")
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_PASS" in out


def test_cmd_tag_missing_file_prints_error(tmp_path: Path, capsys) -> None:
    args = make_args(file=str(tmp_path / "missing.env"), tag_action="list", key=None)
    cmd_tag(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_build_tag_subparser_registers_command() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    build_tag_subparser(subparsers)
    args = parser.parse_args(["tag", ".env", "list"])
    assert args.tag_action == "list"
