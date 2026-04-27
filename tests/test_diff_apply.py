"""Tests for envoy.diff_apply."""
from __future__ import annotations

import pytest

from envoy.diff import ChangeType, EnvDiff, compute_diff
from envoy.diff_apply import ApplyResult, apply_diff, apply_diff_files


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _diff(source: dict, reference: dict) -> EnvDiff:
    return compute_diff(source, reference)


# ---------------------------------------------------------------------------
# apply_diff unit tests
# ---------------------------------------------------------------------------

def test_apply_diff_adds_new_key():
    base = {"A": "1"}
    diff = _diff({}, {"B": "2"})
    updated, result = apply_diff(base, diff)
    assert updated["B"] == "2"
    assert "B" in result.applied


def test_apply_diff_removes_deleted_key():
    base = {"A": "1", "B": "2"}
    diff = _diff({"B": "2"}, {})
    updated, result = apply_diff(base, diff, remove_deleted=True)
    assert "B" not in updated
    assert "B" in result.removed


def test_apply_diff_keep_removed_skips_deletion():
    base = {"A": "1", "B": "2"}
    diff = _diff({"B": "2"}, {})
    updated, result = apply_diff(base, diff, remove_deleted=False)
    assert "B" in updated
    assert "B" in result.skipped


def test_apply_diff_changed_key_without_overwrite_is_conflict():
    base = {"A": "old"}
    diff = _diff({"A": "old"}, {"A": "new"})
    updated, result = apply_diff(base, diff, overwrite=False)
    assert updated["A"] == "old"
    assert "A" in result.conflicts


def test_apply_diff_changed_key_with_overwrite_applies():
    base = {"A": "old"}
    diff = _diff({"A": "old"}, {"A": "new"})
    updated, result = apply_diff(base, diff, overwrite=True)
    assert updated["A"] == "new"
    assert "A" in result.applied


def test_apply_diff_added_key_existing_without_overwrite_skips():
    base = {"B": "existing"}
    diff = _diff({}, {"B": "new"})
    updated, result = apply_diff(base, diff, overwrite=False)
    assert updated["B"] == "existing"
    assert "B" in result.skipped


def test_apply_diff_preserves_untouched_keys():
    base = {"X": "keep", "A": "1"}
    diff = _diff({}, {"B": "2"})
    updated, _ = apply_diff(base, diff)
    assert updated["X"] == "keep"
    assert updated["A"] == "1"


def test_apply_result_repr():
    r = ApplyResult(applied=["A"], skipped=["B"], removed=["C"], conflicts=["D"])
    assert "applied=1" in repr(r)
    assert "skipped=1" in repr(r)


def test_apply_result_has_conflicts_false_when_empty():
    r = ApplyResult()
    assert not r.has_conflicts


def test_apply_result_has_conflicts_true_when_present():
    r = ApplyResult(conflicts=["KEY"])
    assert r.has_conflicts


# ---------------------------------------------------------------------------
# apply_diff_files integration tests
# ---------------------------------------------------------------------------

def test_apply_diff_files_writes_output(tmp_path):
    base_file = tmp_path / "base.env"
    source_file = tmp_path / "source.env"
    ref_file = tmp_path / "ref.env"
    out_file = tmp_path / "out.env"

    base_file.write_text("A=1\nB=2\n")
    source_file.write_text("A=1\n")
    ref_file.write_text("A=1\nC=3\n")

    result = apply_diff_files(
        str(base_file), str(source_file), str(ref_file), output_path=str(out_file)
    )

    content = out_file.read_text()
    assert "C=3" in content
    assert result.total_applied == 1


def test_apply_diff_files_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        apply_diff_files(
            str(tmp_path / "missing.env"),
            str(tmp_path / "source.env"),
            str(tmp_path / "ref.env"),
        )
