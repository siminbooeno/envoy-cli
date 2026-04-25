"""Tests for envoy/copy.py"""

import pytest
from envoy.copy import copy_keys, copy_env_file, CopyResult


SOURCE = {"APP_NAME": "myapp", "DB_HOST": "localhost", "SECRET_KEY": "abc123"}
TARGET = {"APP_NAME": "existing", "PORT": "8080"}


def test_copy_keys_copies_requested_keys():
    output, result = copy_keys(SOURCE, TARGET, ["DB_HOST"], overwrite=False)
    assert output["DB_HOST"] == "localhost"
    assert result.total_copied == 1
    assert "DB_HOST" in result.copied


def test_copy_keys_skips_existing_without_overwrite():
    output, result = copy_keys(SOURCE, TARGET, ["APP_NAME"], overwrite=False)
    assert output["APP_NAME"] == "existing"
    assert result.total_skipped == 1
    assert "APP_NAME" in result.skipped


def test_copy_keys_overwrites_when_flag_set():
    output, result = copy_keys(SOURCE, TARGET, ["APP_NAME"], overwrite=True)
    assert output["APP_NAME"] == "myapp"
    assert result.total_copied == 1


def test_copy_keys_reports_missing_keys():
    output, result = copy_keys(SOURCE, TARGET, ["NONEXISTENT"], overwrite=False)
    assert result.total_missing == 1
    assert "NONEXISTENT" in result.missing


def test_copy_keys_preserves_existing_target_keys():
    output, result = copy_keys(SOURCE, TARGET, ["DB_HOST"])
    assert output["PORT"] == "8080"


def test_copy_keys_multiple_keys_mixed():
    output, result = copy_keys(
        SOURCE, TARGET, ["DB_HOST", "APP_NAME", "MISSING"], overwrite=False
    )
    assert result.total_copied == 1
    assert result.total_skipped == 1
    assert result.total_missing == 1


def test_copy_result_repr():
    r = CopyResult(copied=["A"], skipped=["B"], missing=["C"])
    assert "CopyResult" in repr(r)
    assert "copied=1" in repr(r)


def test_copy_env_file_writes_result(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    src.write_text("DB_HOST=localhost\nSECRET=abc\n")
    tgt.write_text("PORT=8080\n")

    result = copy_env_file(str(src), str(tgt), ["DB_HOST"])
    assert result.total_copied == 1
    content = tgt.read_text()
    assert "DB_HOST=localhost" in content
    assert "PORT=8080" in content


def test_copy_env_file_to_separate_output(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    out = tmp_path / "output.env"
    src.write_text("KEY=value\n")
    tgt.write_text("OTHER=1\n")

    copy_env_file(str(src), str(tgt), ["KEY"], dest_path=str(out))
    content = out.read_text()
    assert "KEY=value" in content
