"""Tests for envoy.cli_merge."""

import argparse
import pytest
from envoy.cli_merge import cmd_merge, build_merge_subparser


@pytest.fixture
def env_a(tmp_path):
    p = tmp_path / "a.env"
    p.write_text("HOST=localhost\nPORT=5432\n")
    return str(p)


@pytest.fixture
def env_b(tmp_path):
    p = tmp_path / "b.env"
    p.write_text("PORT=9999\nDEBUG=true\n")
    return str(p)


def make_args(**kwargs):
    defaults = dict(
        files=[],
        output=None,
        strategy="last",
        dry_run=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_merge_dry_run_prints_output(capsys, env_a, env_b):
    args = make_args(files=[env_a, env_b], dry_run=True)
    cmd_merge(args)
    out = capsys.readouterr().out
    assert "HOST" in out
    assert "DEBUG" in out


def test_cmd_merge_writes_file(tmp_path, env_a, env_b, capsys):
    out = str(tmp_path / "merged.env")
    args = make_args(files=[env_a, env_b], output=out)
    cmd_merge(args)
    content = open(out).read()
    assert "PORT=9999" in content
    captured = capsys.readouterr().out
    assert "merged" in captured


def test_cmd_merge_conflict_exits(capsys, env_a, env_b):
    args = make_args(files=[env_a, env_b], strategy="strict")
    with pytest.raises(SystemExit) as exc_info:
        cmd_merge(args)
    assert exc_info.value.code == 1


def test_cmd_merge_missing_file_exits(capsys, env_a):
    args = make_args(files=[env_a, "/no/such/file.env"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_merge(args)
    assert exc_info.value.code == 1


def test_build_merge_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_merge_subparser(sub)
    parsed = parser.parse_args(["merge", "a.env", "b.env", "--strategy", "first"])
    assert parsed.strategy == "first"
    assert parsed.files == ["a.env", "b.env"]
