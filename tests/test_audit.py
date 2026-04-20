"""Tests for envoy.audit module."""

import json
import pytest
from pathlib import Path
from envoy.audit import log_event, read_log, clear_log, AUDIT_LOG_FILE


@pytest.fixture
def audit_dir(tmp_path):
    return str(tmp_path)


def test_log_event_creates_file(audit_dir):
    log_event("sync", ".env", directory=audit_dir)
    assert (Path(audit_dir) / AUDIT_LOG_FILE).exists()


def test_log_event_returns_entry(audit_dir):
    entry = log_event("encrypt", ".env", details={"keys": 3}, directory=audit_dir)
    assert entry["action"] == "encrypt"
    assert entry["target"] == ".env"
    assert entry["details"]["keys"] == 3
    assert "timestamp" in entry


def test_log_event_appends_multiple(audit_dir):
    log_event("sync", ".env", directory=audit_dir)
    log_event("diff", ".env.staging", directory=audit_dir)
    entries = read_log(audit_dir)
    assert len(entries) == 2
    assert entries[0]["action"] == "sync"
    assert entries[1]["action"] == "diff"


def test_read_log_empty_when_no_file(audit_dir):
    entries = read_log(audit_dir)
    assert entries == []


def test_read_log_parses_json_correctly(audit_dir):
    log_event("mask", ".env", details={"masked": ["SECRET", "API_KEY"]}, directory=audit_dir)
    entries = read_log(audit_dir)
    assert len(entries) == 1
    assert entries[0]["details"]["masked"] == ["SECRET", "API_KEY"]


def test_clear_log_removes_file(audit_dir):
    log_event("sync", ".env", directory=audit_dir)
    log_event("diff", ".env", directory=audit_dir)
    count = clear_log(audit_dir)
    assert count == 2
    assert not (Path(audit_dir) / AUDIT_LOG_FILE).exists()


def test_clear_log_no_file_returns_zero(audit_dir):
    count = clear_log(audit_dir)
    assert count == 0


def test_log_event_timestamp_is_utc_iso(audit_dir):
    entry = log_event("keygen", "secret.key", directory=audit_dir)
    ts = entry["timestamp"]
    assert ts.endswith("+00:00") or ts.endswith("Z")
