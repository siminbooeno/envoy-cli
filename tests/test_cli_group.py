"""Tests for envoy/cli_group.py"""

import argparse
import pytest
from pathlib import Path

from envoy.cli_group import cmd_group, build_group_subparser
from envoy.group import add_to_group, load_groups


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc\n")
    return f


def make_args(env_file: Path, action: str, group: str = "", keys=None, **kwargs):
    ns = argparse.Namespace(
        file=str(env_file),
        group_action=action,
        group=group,
        keys=keys or [],
        **kwargs,
    )
    return ns


def test_cmd_group_add_prints_confirmation(env_file: Path, capsys):
    args = make_args(env_file, "add", group="database", keys=["DB_HOST", "DB_PORT"])
    cmd_group(args)
    out = capsys.readouterr().out
    assert "database" in out
    assert "DB_HOST" in out


def test_cmd_group_add_persists(env_file: Path, capsys):
    args = make_args(env_file, "add", group="database", keys=["DB_HOST"])
    cmd_group(args)
    groups = load_groups(env_file)
    assert "DB_HOST" in groups["database"]


def test_cmd_group_list_shows_groups(env_file: Path, capsys):
    add_to_group(env_file, "database", ["DB_HOST"])
    add_to_group(env_file, "secrets", ["SECRET_KEY"])
    args = make_args(env_file, "list")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "database" in out
    assert "secrets" in out


def test_cmd_group_list_empty_message(env_file: Path, capsys):
    args = make_args(env_file, "list")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "No groups defined" in out


def test_cmd_group_show_existing(env_file: Path, capsys):
    add_to_group(env_file, "database", ["DB_HOST", "DB_PORT"])
    args = make_args(env_file, "show", group="database")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_cmd_group_show_missing(env_file: Path, capsys):
    args = make_args(env_file, "show", group="ghost")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_group_delete_existing(env_file: Path, capsys):
    add_to_group(env_file, "database", ["DB_HOST"])
    args = make_args(env_file, "delete", group="database")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "Deleted" in out
    assert load_groups(env_file) == {}


def test_cmd_group_delete_missing(env_file: Path, capsys):
    args = make_args(env_file, "delete", group="ghost")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_group_missing_file_prints_error(tmp_path: Path, capsys):
    missing = tmp_path / "missing.env"
    args = make_args(missing, "list")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_build_group_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    build_group_subparser(sub)
    assert any(s == "group" for s in sub.choices)
