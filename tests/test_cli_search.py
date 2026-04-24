"""Tests for envoy.cli_search."""
import argparse
import pytest

from envoy.cli_search import cmd_search, build_search_subparser


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "API_KEY=supersecret\n"
        "DATABASE_URL=postgres://localhost/db\n"
        "DEBUG=true\n"
    )
    return str(p)


def make_args(**kwargs):
    defaults = dict(
        file=None,
        pattern="",
        keys_only=False,
        values_only=False,
        case_sensitive=False,
        exact=False,
        masked=False,
        verbose=False,
        fail_on_no_match=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_search_finds_match(env_file, capsys):
    args = make_args(file=env_file, pattern="DEBUG")
    cmd_search(args)
    out = capsys.readouterr().out
    assert "DEBUG" in out
    assert "1 match" in out


def test_cmd_search_no_match(env_file, capsys):
    args = make_args(file=env_file, pattern="NONEXISTENT")
    cmd_search(args)
    out = capsys.readouterr().out
    assert "No matches found" in out


def test_cmd_search_masked_hides_secret(env_file, capsys):
    args = make_args(file=env_file, pattern="API_KEY", masked=True)
    cmd_search(args)
    out = capsys.readouterr().out
    assert "supersecret" not in out
    assert "***" in out


def test_cmd_search_verbose_shows_flags(env_file, capsys):
    args = make_args(file=env_file, pattern="DEBUG", verbose=True)
    cmd_search(args)
    out = capsys.readouterr().out
    assert "key" in out or "value" in out


def test_cmd_search_missing_file_exits(tmp_path, capsys):
    args = make_args(file=str(tmp_path / "missing.env"), pattern="X")
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(args)
    assert exc_info.value.code == 1


def test_cmd_search_fail_on_no_match_exits(env_file):
    args = make_args(file=env_file, pattern="NONEXISTENT", fail_on_no_match=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_search(args)
    assert exc_info.value.code == 2


def test_build_search_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_search_subparser(subs)
    args = parser.parse_args(["search", ".env", "KEY"])
    assert args.pattern == "KEY"
    assert args.file == ".env"
