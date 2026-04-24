"""Unit tests for envoy.patch."""

import pytest

from envoy.patch import patch_env, patch_env_file


# ---------------------------------------------------------------------------
# patch_env (pure dict API)
# ---------------------------------------------------------------------------

def test_patch_env_adds_new_key():
    env = {"A": "1"}
    result, report = patch_env(env, {"B": "2"})
    assert result["B"] == "2"
    assert "B" in report.added


def test_patch_env_updates_existing_key():
    env = {"A": "1"}
    result, report = patch_env(env, {"A": "99"})
    assert result["A"] == "99"
    assert "A" in report.updated


def test_patch_env_skips_existing_without_overwrite():
    env = {"A": "1"}
    result, report = patch_env(env, {"A": "99"}, overwrite=False)
    assert result["A"] == "1"
    assert "A" in report.skipped


def test_patch_env_removes_key_when_value_is_none():
    env = {"A": "1", "B": "2"}
    result, report = patch_env(env, {"A": None})
    assert "A" not in result
    assert "A" in report.removed


def test_patch_env_skips_remove_when_key_absent():
    env = {"B": "2"}
    result, report = patch_env(env, {"MISSING": None})
    assert "MISSING" not in result
    assert "MISSING" in report.skipped


def test_patch_env_does_not_mutate_original():
    env = {"A": "1"}
    patch_env(env, {"A": "2"})
    assert env["A"] == "1"


def test_patch_env_total_changed():
    env = {"A": "1", "B": "2"}
    _, report = patch_env(env, {"A": "9", "C": "3", "B": None})
    assert report.total_changed == 3


def test_patch_env_remove_nulls_false_treats_none_as_literal():
    env = {"A": "1"}
    result, report = patch_env(env, {"A": None}, remove_nulls=False)
    # None is assigned as the value (caller's responsibility)
    assert result["A"] is None
    assert "A" in report.updated


# ---------------------------------------------------------------------------
# patch_env_file (file I/O)
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP=hello\nDEBUG=false\n")
    return str(p)


def test_patch_env_file_updates_value(env_file):
    report = patch_env_file(env_file, {"APP": "world"})
    assert "APP" in report.updated
    content = open(env_file).read()
    assert "APP=world" in content


def test_patch_env_file_adds_key(env_file):
    report = patch_env_file(env_file, {"NEW_KEY": "42"})
    assert "NEW_KEY" in report.added
    assert "NEW_KEY=42" in open(env_file).read()


def test_patch_env_file_removes_key(env_file):
    report = patch_env_file(env_file, {"DEBUG": None})
    assert "DEBUG" in report.removed
    assert "DEBUG" not in open(env_file).read()


def test_patch_env_file_dry_run_does_not_write(env_file):
    original = open(env_file).read()
    patch_env_file(env_file, {"APP": "changed"}, dry_run=True)
    assert open(env_file).read() == original


def test_patch_env_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        patch_env_file(str(tmp_path / "ghost.env"), {"X": "1"})
