"""Tests for envoy.compare module."""

import pytest
from pathlib import Path

from envoy.compare import compare_env_files, format_report, CompareReport


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.source"
    f.write_text(
        "APP_NAME=myapp\n"
        "DB_HOST=localhost\n"
        "SECRET_KEY=supersecret\n"
        "ONLY_IN_SOURCE=yes\n"
    )
    return f


@pytest.fixture
def target_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.target"
    f.write_text(
        "APP_NAME=myapp\n"
        "DB_HOST=remotehost\n"
        "SECRET_KEY=othersecret\n"
        "ONLY_IN_TARGET=yes\n"
    )
    return f


def test_compare_detects_added_key(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    assert "ONLY_IN_SOURCE" in report.source_only


def test_compare_detects_removed_key(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    assert "ONLY_IN_TARGET" in report.target_only


def test_compare_detects_changed_key(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    assert "DB_HOST" in report.changed


def test_compare_common_keys(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    assert "APP_NAME" in report.common


def test_compare_has_differences(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    assert report.has_differences is True


def test_compare_no_differences(tmp_path):
    content = "KEY=value\nOTHER=hello\n"
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text(content)
    b.write_text(content)
    report = compare_env_files(str(a), str(b))
    assert report.has_differences is False
    assert report.summary["common"] == 2


def test_compare_masks_secrets(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file), mask_secrets=True)
    for diff in report.diffs:
        if diff.key == "SECRET_KEY":
            if diff.old_value is not None:
                assert diff.old_value != "supersecret"
            if diff.new_value is not None:
                assert diff.new_value != "othersecret"


def test_format_report_contains_summary(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    output = format_report(report)
    assert "Added" in output
    assert "Removed" in output
    assert "Changed" in output


def test_format_report_verbose_shows_keys(source_file, target_file):
    report = compare_env_files(str(source_file), str(target_file))
    output = format_report(report, verbose=True)
    assert "DB_HOST" in output


def test_missing_source_raises(tmp_path, target_file):
    with pytest.raises(FileNotFoundError):
        compare_env_files(str(tmp_path / "missing.env"), str(target_file))
