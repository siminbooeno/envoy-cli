"""Tests for envoy/import_env.py"""

import json
import os
import pytest

from envoy.import_env import (
    import_from_os,
    import_from_json,
    import_from_dotenv_string,
    merge_imported,
)


# ---------------------------------------------------------------------------
# import_from_os
# ---------------------------------------------------------------------------

def test_import_from_os_returns_dict(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "hello")
    result = import_from_os()
    assert "SOME_VAR" in result
    assert result["SOME_VAR"] == "hello"


def test_import_from_os_with_prefix(monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("OTHER_VAR", "ignored")
    result = import_from_os(prefix="APP_")
    assert "HOST" in result
    assert "PORT" in result
    assert "OTHER_VAR" not in result
    assert "APP_HOST" not in result


def test_import_from_os_prefix_no_empty_keys(monkeypatch):
    monkeypatch.setenv("PREFIX_", "value")  # key would become empty string
    result = import_from_os(prefix="PREFIX_")
    assert "" not in result


# ---------------------------------------------------------------------------
# import_from_json
# ---------------------------------------------------------------------------

def test_import_from_json_flat_object(tmp_path):
    data = {"DB_HOST": "localhost", "DB_PORT": 5432, "DEBUG": True}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    result = import_from_json(str(p))
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DEBUG"] == "true"


def test_import_from_json_raises_on_non_object(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ValueError, match="Expected a JSON object"):
        import_from_json(str(p))


def test_import_from_json_raises_on_nested(tmp_path):
    p = tmp_path / "nested.json"
    p.write_text(json.dumps({"DB": {"host": "localhost"}}))
    with pytest.raises(ValueError, match="Nested objects"):
        import_from_json(str(p))


# ---------------------------------------------------------------------------
# import_from_dotenv_string
# ---------------------------------------------------------------------------

def test_import_from_dotenv_string_basic():
    content = "HOST=localhost\nPORT=3000\n"
    result = import_from_dotenv_string(content)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "3000"


def test_import_from_dotenv_string_ignores_comments():
    content = "# comment\nKEY=value\n"
    result = import_from_dotenv_string(content)
    assert "KEY" in result
    assert len(result) == 1


# ---------------------------------------------------------------------------
# merge_imported
# ---------------------------------------------------------------------------

def test_merge_imported_adds_new_keys():
    base = {"A": "1"}
    imported = {"B": "2"}
    result = merge_imported(base, imported)
    assert result == {"A": "1", "B": "2"}


def test_merge_imported_no_overwrite_by_default():
    base = {"A": "original"}
    imported = {"A": "new"}
    result = merge_imported(base, imported, overwrite=False)
    assert result["A"] == "original"


def test_merge_imported_overwrite_flag():
    base = {"A": "original"}
    imported = {"A": "new"}
    result = merge_imported(base, imported, overwrite=True)
    assert result["A"] == "new"


def test_merge_imported_does_not_mutate_base():
    base = {"A": "1"}
    imported = {"B": "2"}
    merge_imported(base, imported)
    assert "B" not in base
