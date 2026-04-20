"""Tests for envoy.lint module."""

import pytest
from pathlib import Path

from envoy.lint import lint_env_file, LintResult, LintIssue, Severity


@pytest.fixture
def tmp_env(tmp_path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_clean_file_returns_no_issues(tmp_env):
    path = tmp_env("APP_NAME=myapp\nDEBUG=false\n")
    result = lint_env_file(path)
    assert not result.issues
    assert not result.has_errors
    assert not result.has_warnings


def test_lowercase_key_triggers_warning(tmp_env):
    path = tmp_env("app_name=myapp\n")
    result = lint_env_file(path)
    keys_msgs = [(i.key, i.severity) for i in result.issues]
    assert any(k == "app_name" and s == Severity.WARNING for k, s in keys_msgs)


def test_duplicate_key_triggers_error(tmp_env):
    path = tmp_env("APP=1\nAPP=2\n")
    result = lint_env_file(path)
    assert result.has_errors
    dup = [i for i in result.issues if "Duplicate" in i.message]
    assert len(dup) == 1


def test_invalid_line_triggers_error(tmp_env):
    path = tmp_env("INVALID_LINE_NO_EQUALS\n")
    result = lint_env_file(path)
    assert result.has_errors
    assert any("valid KEY=VALUE" in i.message for i in result.issues)


def test_secret_empty_value_triggers_warning(tmp_env):
    path = tmp_env("SECRET_KEY=\n")
    result = lint_env_file(path)
    assert result.has_warnings
    assert any("empty value" in i.message for i in result.issues)


def test_comments_and_blank_lines_ignored(tmp_env):
    path = tmp_env("# This is a comment\n\nAPP=ok\n")
    result = lint_env_file(path)
    assert not result.issues


def test_summary_string(tmp_env):
    path = tmp_env("INVALID\napp=low\n")
    result = lint_env_file(path)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_issue_str_representation():
    issue = LintIssue(line=3, key="FOO", message="test msg", severity=Severity.ERROR)
    s = str(issue)
    assert "ERROR" in s
    assert "FOO" in s
    assert "test msg" in s
    assert "3" in s


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        lint_env_file("/nonexistent/.env")
