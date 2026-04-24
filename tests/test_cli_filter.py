"""Tests for envoy.cli_filter module."""
import argparse
import pytest
from pathlib import Path
from envoy.cli_filter import cmd_filter, build_filter_subparser
from envoy.parser import serialize_env


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "APP_ENV=staging\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "SECRET_KEY=topsecret\n"
        "EMPTY_VAR=\n"
    )
    return str(p)


def make_args(**kwargs):
    defaults = dict(
        file=None,
        prefix=None,
        pattern=None,
        value_pattern=None,
        exclude_empty=False,
        output=None,
        masked=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_filter_prefix_prints_matching(env_file, capsys):
    args = make_args(file=env_file, prefix="APP_")
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out
    assert "APP_ENV=staging" in out
    assert "DB_HOST" not in out


def test_cmd_filter_no_match_prints_message(env_file, capsys):
    args = make_args(file=env_file, prefix="NONEXISTENT_")
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "No keys matched" in out


def test_cmd_filter_writes_output_file(env_file, tmp_path):
    out_path = str(tmp_path / "filtered.env")
    args = make_args(file=env_file, prefix="DB_", output=out_path)
    cmd_filter(args)
    content = Path(out_path).read_text()
    assert "DB_HOST" in content
    assert "APP_NAME" not in content


def test_cmd_filter_verbose_shows_counts(env_file, capsys):
    args = make_args(file=env_file, prefix="APP_", verbose=True)
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "matched" in out or "excluded" in out


def test_cmd_filter_masked_hides_secret(env_file, capsys):
    args = make_args(file=env_file, pattern="SECRET", masked=True)
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "topsecret" not in out
    assert "SECRET_KEY" in out


def test_cmd_filter_missing_file_exits(tmp_path, capsys):
    args = make_args(file=str(tmp_path / "missing.env"))
    with pytest.raises(SystemExit):
        cmd_filter(args)
    err = capsys.readouterr().err
    assert "not found" in err


def test_build_filter_subparser_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_filter_subparser(sub)
    args = parser.parse_args(["filter", "myfile.env", "--prefix", "APP_"])
    assert args.prefix == "APP_"
    assert args.file == "myfile.env"
