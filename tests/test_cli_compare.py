"""Tests for envoy.cli_compare module."""

import argparse
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.cli_compare import cmd_compare, build_compare_subparser


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.source"
    f.write_text("APP=myapp\nDB_HOST=localhost\nAPI_SECRET=abc123\n")
    return f


@pytest.fixture
def target_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.target"
    f.write_text("APP=myapp\nDB_HOST=remotehost\nNEW_KEY=new\n")
    return f


def make_args(**kwargs):
    defaults = {
        "source": "",
        "target": "",
        "mask": False,
        "verbose": False,
        "exit_code": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_compare_prints_summary(source_file, target_file, capsys):
    args = make_args(source=str(source_file), target=str(target_file))
    with patch("envoy.cli_compare.log_event"):
        cmd_compare(args)
    captured = capsys.readouterr()
    assert "Added" in captured.out
    assert "Removed" in captured.out


def test_cmd_compare_verbose_shows_keys(source_file, target_file, capsys):
    args = make_args(source=str(source_file), target=str(target_file), verbose=True)
    with patch("envoy.cli_compare.log_event"):
        cmd_compare(args)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out


def test_cmd_compare_exit_code_on_diff(source_file, target_file):
    args = make_args(source=str(source_file), target=str(target_file), exit_code=True)
    with patch("envoy.cli_compare.log_event"):
        with pytest.raises(SystemExit) as exc_info:
            cmd_compare(args)
    assert exc_info.value.code == 1


def test_cmd_compare_no_exit_code_when_identical(tmp_path):
    content = "KEY=val\n"
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(content)
    b.write_text(content)
    args = make_args(source=str(a), target=str(b), exit_code=True)
    with patch("envoy.cli_compare.log_event"):
        cmd_compare(args)  # should NOT raise SystemExit


def test_cmd_compare_missing_file_exits(tmp_path, target_file, capsys):
    args = make_args(source=str(tmp_path / "nope.env"), target=str(target_file))
    with pytest.raises(SystemExit) as exc_info:
        cmd_compare(args)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_build_compare_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    build_compare_subparser(subparsers)
    args = parser.parse_args(["compare", "src.env", "tgt.env", "--mask", "--verbose"])
    assert args.source == "src.env"
    assert args.target == "tgt.env"
    assert args.mask is True
    assert args.verbose is True
