"""Integration tests for envoy.cli_patch."""

import argparse
import pytest

from envoy.cli_patch import cmd_patch, build_patch_subparser


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP=hello\nDEBUG=false\n")
    return str(p)


def make_args(**kwargs):
    defaults = {
        "set": None,
        "remove": None,
        "no_overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_patch_adds_key(env_file, capsys):
    args = make_args(file=env_file, set=["NEW=123"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "+ NEW" in out
    assert "NEW=123" in open(env_file).read()


def test_cmd_patch_updates_key(env_file, capsys):
    args = make_args(file=env_file, set=["APP=world"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "~ APP" in out


def test_cmd_patch_removes_key(env_file, capsys):
    args = make_args(file=env_file, remove=["DEBUG"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "- DEBUG" in out
    assert "DEBUG" not in open(env_file).read()


def test_cmd_patch_dry_run_prints_preview(env_file, capsys):
    original = open(env_file).read()
    args = make_args(file=env_file, set=["APP=changed"], dry_run=True)
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert open(env_file).read() == original


def test_cmd_patch_no_overwrite_skips(env_file, capsys):
    args = make_args(file=env_file, set=["APP=ignored"], no_overwrite=True)
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "skipped" in out
    assert "APP=hello" in open(env_file).read()


def test_cmd_patch_missing_file_exits(tmp_path):
    args = make_args(file=str(tmp_path / "ghost.env"), set=["X=1"])
    with pytest.raises(SystemExit):
        cmd_patch(args)


def test_cmd_patch_no_args_exits(env_file):
    args = make_args(file=env_file)
    with pytest.raises(SystemExit):
        cmd_patch(args)


def test_cmd_patch_bad_set_format_exits(env_file):
    args = make_args(file=env_file, set=["BADFORMAT"])
    with pytest.raises(SystemExit):
        cmd_patch(args)


def test_build_patch_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_patch_subparser(subs)
    parsed = parser.parse_args(["patch", "my.env", "--set", "K=V"])
    assert parsed.file == "my.env"
    assert parsed.set == ["K=V"]
