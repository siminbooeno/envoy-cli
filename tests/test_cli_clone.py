"""Tests for envoy.cli_clone module."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envoy.cli_clone import cmd_clone, build_clone_subparser
from envoy.parser import load_env_file


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / "source.env"
    f.write_text("APP_NAME=myapp\nDB_PASSWORD=s3cr3t\nDEBUG=true\n")
    return f


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "source": "",
        "destination": "",
        "include": None,
        "exclude": None,
        "masked": False,
        "overwrite": False,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_clone_creates_file(source_file: Path, tmp_path: Path, capsys):
    dest = tmp_path / "dest.env"
    args = make_args(source=str(source_file), destination=str(dest))
    cmd_clone(args)
    assert dest.exists()
    captured = capsys.readouterr()
    assert "Cloned" in captured.out
    assert "3 key(s)" in captured.out


def test_cmd_clone_verbose_shows_keys(source_file: Path, tmp_path: Path, capsys):
    dest = tmp_path / "dest.env"
    args = make_args(source=str(source_file), destination=str(dest), verbose=True)
    cmd_clone(args)
    captured = capsys.readouterr()
    assert "APP_NAME" in captured.out


def test_cmd_clone_missing_source_prints_error(tmp_path: Path, capsys):
    args = make_args(source=str(tmp_path / "missing.env"), destination=str(tmp_path / "dest.env"))
    cmd_clone(args)
    captured = capsys.readouterr()
    assert "[error]" in captured.out


def test_cmd_clone_existing_dest_no_overwrite_prints_error(source_file: Path, tmp_path: Path, capsys):
    dest = tmp_path / "dest.env"
    dest.write_text("X=1\n")
    args = make_args(source=str(source_file), destination=str(dest), overwrite=False)
    cmd_clone(args)
    captured = capsys.readouterr()
    assert "[error]" in captured.out


def test_cmd_clone_with_exclude(source_file: Path, tmp_path: Path, capsys):
    dest = tmp_path / "dest.env"
    args = make_args(source=str(source_file), destination=str(dest), exclude="DB_PASSWORD")
    cmd_clone(args)
    env = load_env_file(str(dest))
    assert "DB_PASSWORD" not in env
    captured = capsys.readouterr()
    assert "Skipped" in captured.out


def test_build_clone_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_clone_subparser(subparsers)
    args = parser.parse_args(["clone", "src.env", "dst.env", "--masked"])
    assert args.masked is True
    assert args.source == "src.env"
    assert args.destination == "dst.env"
