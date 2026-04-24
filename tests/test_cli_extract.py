"""Tests for envoy.cli_extract module."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envoy.cli_extract import cmd_extract, build_extract_subparser


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nDB_URL=postgres://localhost/db\nDEBUG=false\n")
    return f


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "source": "",
        "keys": "",
        "output": None,
        "overwrite": False,
        "ignore_missing": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_extract_dry_run_prints_keys(env_file: Path, capsys):
    args = make_args(source=str(env_file), keys="API_KEY,DEBUG", dry_run=True)
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "API_KEY=secret" in out
    assert "DEBUG=false" in out
    assert "dry-run" in out


def test_cmd_extract_writes_output_file(env_file: Path, tmp_path: Path, capsys):
    dest = tmp_path / "out.env"
    args = make_args(source=str(env_file), keys="DB_URL", output=str(dest))
    cmd_extract(args)
    assert dest.exists()
    assert "DB_URL" in dest.read_text()
    out = capsys.readouterr().out
    assert "[ok]" in out


def test_cmd_extract_missing_key_prints_error(env_file: Path, capsys):
    args = make_args(source=str(env_file), keys="DOES_NOT_EXIST")
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "[missing]" in out
    assert "[error]" in out


def test_cmd_extract_missing_source_prints_error(tmp_path: Path, capsys):
    args = make_args(source=str(tmp_path / "ghost.env"), keys="A")
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "[error]" in out
    assert "not found" in out


def test_cmd_extract_ignore_missing_flag(env_file: Path, capsys):
    args = make_args(source=str(env_file), keys="API_KEY,GHOST_KEY", ignore_missing=True, dry_run=True)
    cmd_extract(args)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "GHOST_KEY" not in out


def test_build_extract_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_extract_subparser(subparsers)
    args = parser.parse_args(["extract", "some.env", "KEY1,KEY2", "--dry-run"])
    assert args.dry_run is True
    assert args.keys == "KEY1,KEY2"
