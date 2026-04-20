"""Tests for envoy.cli_audit commands."""

import argparse
import pytest
from envoy.audit import log_event, AUDIT_LOG_FILE
from envoy.cli_audit import cmd_audit_log, cmd_audit_clear
from pathlib import Path


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path


def make_args(**kwargs):
    defaults = {"dir": None, "action": None, "limit": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_audit_log_empty(audit_dir, capsys):
    args = make_args(dir=str(audit_dir))
    cmd_audit_log(args)
    captured = capsys.readouterr()
    assert "No audit log entries found" in captured.out


def test_cmd_audit_log_shows_entries(audit_dir, capsys):
    log_event("sync", ".env", details={"added": 2}, directory=str(audit_dir))
    log_event("diff", ".env.prod", directory=str(audit_dir))
    args = make_args(dir=str(audit_dir))
    cmd_audit_log(args)
    captured = capsys.readouterr()
    assert "sync" in captured.out
    assert "diff" in captured.out
    assert ".env.prod" in captured.out


def test_cmd_audit_log_filter_by_action(audit_dir, capsys):
    log_event("sync", ".env", directory=str(audit_dir))
    log_event("encrypt", ".env", directory=str(audit_dir))
    args = make_args(dir=str(audit_dir), action="encrypt")
    cmd_audit_log(args)
    captured = capsys.readouterr()
    assert "encrypt" in captured.out
    assert "sync" not in captured.out


def test_cmd_audit_log_limit(audit_dir, capsys):
    for i in range(5):
        log_event("diff", f".env.{i}", directory=str(audit_dir))
    args = make_args(dir=str(audit_dir), limit=2)
    cmd_audit_log(args)
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_audit_clear_removes_log(audit_dir, capsys):
    log_event("sync", ".env", directory=str(audit_dir))
    args = make_args(dir=str(audit_dir))
    cmd_audit_clear(args)
    assert not (audit_dir / AUDIT_LOG_FILE).exists()
    captured = capsys.readouterr()
    assert "Cleared 1" in captured.out


def test_cmd_audit_clear_empty_log(audit_dir, capsys):
    args = make_args(dir=str(audit_dir))
    cmd_audit_clear(args)
    captured = capsys.readouterr()
    assert "already empty" in captured.out
