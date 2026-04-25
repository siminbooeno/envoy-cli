"""Tests for envoy/cli_copy.py"""

import argparse
import pytest
from envoy.cli_copy import cmd_copy, build_copy_subparser


@pytest.fixture
def source_file(tmp_path):
    f = tmp_path / "source.env"
    f.write_text("DB_HOST=localhost\nSECRET_KEY=abc123\nAPP_NAME=myapp\n")
    return f


@pytest.fixture
def target_file(tmp_path):
    f = tmp_path / "target.env"
    f.write_text("PORT=8080\nAPP_NAME=existing\n")
    return f


def make_args(**kwargs):
    defaults = {"overwrite": False, "output": None, "dry_run": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_copy_prints_copied_keys(source_file, target_file, capsys):
    args = make_args(source=str(source_file), target=str(target_file), keys=["DB_HOST"])
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "Copied: DB_HOST" in out


def test_cmd_copy_prints_skipped_keys(source_file, target_file, capsys):
    args = make_args(source=str(source_file), target=str(target_file), keys=["APP_NAME"])
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "Skipped" in out
    assert "APP_NAME" in out


def test_cmd_copy_prints_missing_keys(source_file, target_file, capsys):
    args = make_args(source=str(source_file), target=str(target_file), keys=["NONEXISTENT"])
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "Missing in source" in out


def test_cmd_copy_dry_run_does_not_write(source_file, target_file):
    original = target_file.read_text()
    args = make_args(
        source=str(source_file), target=str(target_file),
        keys=["DB_HOST"], dry_run=True
    )
    cmd_copy(args)
    assert target_file.read_text() == original


def test_cmd_copy_dry_run_prints_preview(source_file, target_file, capsys):
    args = make_args(
        source=str(source_file), target=str(target_file),
        keys=["DB_HOST"], dry_run=True
    )
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "DB_HOST" in out


def test_build_copy_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_copy_subparser(subs)
    args = parser.parse_args(["copy", "src.env", "tgt.env", "KEY1", "KEY2"])
    assert args.keys == ["KEY1", "KEY2"]
    assert args.overwrite is False
