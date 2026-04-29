"""Tests for envoy/cli_normalize.py"""

import argparse
import sys
import pytest

from envoy.cli_normalize import cmd_normalize, build_normalize_subparser


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("my-key=  hello  \nCLEAN=value\n")
    return f


def make_args(**kwargs):
    defaults = {
        "file": "",
        "no_keys": False,
        "no_values": False,
        "lowercase_values": False,
        "only": None,
        "dry_run": False,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_normalize_prints_summary(env_file, capsys):
    args = make_args(file=str(env_file))
    cmd_normalize(args)
    out = capsys.readouterr().out
    assert "Normalized" in out


def test_cmd_normalize_dry_run_prints_preview(env_file, capsys):
    args = make_args(file=str(env_file), dry_run=True)
    cmd_normalize(args)
    out = capsys.readouterr().out
    assert "dry-run" in out
    # File should not be modified
    content = env_file.read_text()
    assert "my-key" in content


def test_cmd_normalize_verbose_shows_changes(env_file, capsys):
    args = make_args(file=str(env_file), verbose=True)
    cmd_normalize(args)
    out = capsys.readouterr().out
    assert "->" in out


def test_cmd_normalize_missing_file_exits(tmp_path, capsys):
    args = make_args(file=str(tmp_path / "missing.env"))
    with pytest.raises(SystemExit) as exc:
        cmd_normalize(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_cmd_normalize_no_keys_preserves_case(env_file, capsys):
    args = make_args(file=str(env_file), no_keys=True)
    cmd_normalize(args)
    content = env_file.read_text()
    assert "my-key" in content


def test_build_normalize_subparser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_normalize_subparser(subs)
    args = parser.parse_args(["normalize", "some.env", "--dry-run", "--verbose"])
    assert args.file == "some.env"
    assert args.dry_run is True
    assert args.verbose is True
