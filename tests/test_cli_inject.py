"""Tests for envoy.cli_inject."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from envoy.cli_inject import cmd_inject, build_inject_subparser


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("APP_NAME=myapp\nDEBUG=true\nSECRET_KEY=s3cr3t\n")
    return f


def make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        env_file=None,
        command=[],
        keys=None,
        overwrite=True,
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_inject_dry_run_prints_keys(env_file, capsys):
    args = make_args(env_file=str(env_file))
    cmd_inject(args)
    out = capsys.readouterr().out
    assert "inject" in out.lower() or "key" in out.lower()


def test_cmd_inject_dry_run_with_key_filter(env_file, capsys):
    args = make_args(env_file=str(env_file), keys=["APP_NAME"])
    cmd_inject(args)
    out = capsys.readouterr().out
    assert "APP_NAME" in out
    assert "SECRET_KEY" not in out


def test_cmd_inject_missing_file_exits(tmp_path, capsys):
    args = make_args(env_file=str(tmp_path / "missing.env"))
    with pytest.raises(SystemExit) as exc:
        cmd_inject(args)
    assert exc.value.code == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_inject_runs_command(env_file):
    args = make_args(
        env_file=str(env_file),
        command=[sys.executable, "-c", "import sys; sys.exit(0)"],
        verbose=True,
    )
    with pytest.raises(SystemExit) as exc:
        cmd_inject(args)
    assert exc.value.code == 0


def test_build_inject_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_inject_subparser(subs)
    parsed = parser.parse_args(["inject", ".env"])
    assert parsed.env_file == ".env"
    assert hasattr(parsed, "func")
