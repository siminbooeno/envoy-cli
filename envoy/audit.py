"""Audit log for tracking .env file operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILE = ".envoy_audit.jsonl"


def _audit_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / AUDIT_LOG_FILE


def log_event(
    action: str,
    target: str,
    details: Optional[dict] = None,
    directory: Optional[str] = None,
) -> dict:
    """Append an audit event to the log file and return the entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "target": str(target),
        "details": details or {},
    }
    audit_file = _audit_path(directory)
    with open(audit_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_log(directory: Optional[str] = None) -> list[dict]:
    """Read all audit log entries from the log file."""
    audit_file = _audit_path(directory)
    if not audit_file.exists():
        return []
    entries = []
    with open(audit_file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_log(directory: Optional[str] = None) -> int:
    """Delete the audit log file. Returns number of entries removed."""
    audit_file = _audit_path(directory)
    count = len(read_log(directory))
    if audit_file.exists():
        audit_file.unlink()
    return count
