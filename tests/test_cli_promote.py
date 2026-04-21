"""Tests for envoy.cli_promote module."""

import pytest
from pathlib import Path
from types import SimpleNamespace
from envoy.cli_promote import cmd_promote


@pytest.fixture
def source_file(tmp_path):
    p = tmp_path / "source.env"
    p.write_text("API_KEY=secret\nDB_HOST=prod-db\nNEW_VAR=hello\n")
    return str(p)


@pytest.fixture
def target_file(tmp_path):
    p = tmp_path / "target.env"
    p.write_text("DB_HOST=staging-db\nAPP_ENV=staging\n")
    return str(p)


def make_args(**kwargs):
    defaults = {
        "source": None,
        "target": None,
        "keys": None,
        "overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_promote_prints_promoted_keys(source_file, target_file, capsys):
    args = make_args(source=source_file, target=target_file, keys="NEW_VAR")
    cmd_promote(args)
    out = capsys.readouterr().out
    assert "NEW_VAR" in out
    assert "Promoted" in out


def test_cmd_promote_dry_run_prints_preview(source_file, target_file, capsys):
    original = Path(target_file).read_text()
    args = make_args(source=source_file, target=target_file, keys="NEW_VAR", dry_run=True)
    cmd_promote(args)
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert Path(target_file).read_text() == original


def test_cmd_promote_nothing_to_promote(source_file, target_file, capsys):
    args = make_args(source=source_file, target=target_file, keys="DB_HOST", overwrite=False)
    cmd_promote(args)
    out = capsys.readouterr().out
    assert "Nothing to promote" in out


def test_cmd_promote_overwrite_updates_target(source_file, target_file, capsys):
    args = make_args(source=source_file, target=target_file, keys="DB_HOST", overwrite=True)
    cmd_promote(args)
    content = Path(target_file).read_text()
    assert "DB_HOST=prod-db" in content


def test_cmd_promote_no_keys_promotes_all(source_file, target_file, capsys):
    args = make_args(source=source_file, target=target_file, keys=None, overwrite=True)
    cmd_promote(args)
    content = Path(target_file).read_text()
    assert "API_KEY=secret" in content
    assert "NEW_VAR=hello" in content
