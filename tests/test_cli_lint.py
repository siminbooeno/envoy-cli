"""Tests for envoy.cli_lint module."""

import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.cli_lint import cmd_lint, build_lint_subparser


@pytest.fixture
def env_file(tmp_path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def make_args(file: str, strict: bool = False) -> argparse.Namespace:
    return argparse.Namespace(file=file, strict=strict)


def test_cmd_lint_clean_file_prints_ok(env_file, capsys):
    path = env_file("APP=prod\nDEBUG=false\n")
    cmd_lint(make_args(path))
    out = capsys.readouterr().out
    assert "No issues" in out


def test_cmd_lint_reports_warnings(env_file, capsys):
    path = env_file("app=lower\n")
    cmd_lint(make_args(path))
    out = capsys.readouterr().out
    assert "warning" in out.lower() or "⚠" in out


def test_cmd_lint_reports_errors(env_file, capsys):
    path = env_file("BADLINE\n")
    cmd_lint(make_args(path))
    out = capsys.readouterr().out
    assert "error" in out.lower() or "✖" in out


def test_cmd_lint_strict_exits_on_error(env_file):
    path = env_file("BADLINE\n")
    with pytest.raises(SystemExit) as exc_info:
        cmd_lint(make_args(path, strict=True))
    assert exc_info.value.code == 1


def test_cmd_lint_strict_no_exit_on_clean(env_file):
    path = env_file("APP=ok\n")
    cmd_lint(make_args(path, strict=True))  # should not raise


def test_cmd_lint_missing_file_exits(tmp_path):
    args = make_args(str(tmp_path / "missing.env"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_lint(args)
    assert exc_info.value.code == 1


def test_build_lint_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_lint_subparser(sub)
    args = parser.parse_args(["lint", "myfile.env"])
    assert args.file == "myfile.env"
    assert args.strict is False


def test_build_lint_subparser_strict_flag():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_lint_subparser(sub)
    args = parser.parse_args(["lint", "myfile.env", "--strict"])
    assert args.strict is True
