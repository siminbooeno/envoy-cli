"""Tests for envoy/profile.py"""

import pytest

from envoy.profile import (
    apply_profile,
    delete_profile,
    get_profile,
    list_profiles,
    load_profiles,
    set_profile,
)


@pytest.fixture
def profile_dir(tmp_path):
    return str(tmp_path)


def test_load_profiles_empty_when_no_file(profile_dir):
    assert load_profiles(profile_dir) == {}


def test_set_and_get_profile(profile_dir):
    set_profile("dev", {"DEBUG": "true", "DB_HOST": "localhost"}, profile_dir)
    result = get_profile("dev", profile_dir)
    assert result == {"DEBUG": "true", "DB_HOST": "localhost"}


def test_get_profile_missing_returns_none(profile_dir):
    assert get_profile("nonexistent", profile_dir) is None


def test_set_profile_overwrites_existing(profile_dir):
    set_profile("prod", {"DEBUG": "false"}, profile_dir)
    set_profile("prod", {"DEBUG": "false", "LOG_LEVEL": "error"}, profile_dir)
    result = get_profile("prod", profile_dir)
    assert result == {"DEBUG": "false", "LOG_LEVEL": "error"}


def test_list_profiles_sorted(profile_dir):
    set_profile("staging", {"X": "1"}, profile_dir)
    set_profile("dev", {"X": "2"}, profile_dir)
    set_profile("prod", {"X": "3"}, profile_dir)
    assert list_profiles(profile_dir) == ["dev", "prod", "staging"]


def test_list_profiles_empty(profile_dir):
    assert list_profiles(profile_dir) == []


def test_delete_profile_existing(profile_dir):
    set_profile("dev", {"A": "1"}, profile_dir)
    removed = delete_profile("dev", profile_dir)
    assert removed is True
    assert get_profile("dev", profile_dir) is None


def test_delete_profile_nonexistent(profile_dir):
    removed = delete_profile("ghost", profile_dir)
    assert removed is False


def test_apply_profile_merges_values(profile_dir):
    base = {"APP_ENV": "local", "DB_HOST": "localhost", "DEBUG": "true"}
    set_profile("staging", {"APP_ENV": "staging", "DB_HOST": "staging-db"}, profile_dir)
    result = apply_profile(base, "staging", profile_dir)
    assert result["APP_ENV"] == "staging"
    assert result["DB_HOST"] == "staging-db"
    assert result["DEBUG"] == "true"  # untouched base key


def test_apply_profile_does_not_mutate_base(profile_dir):
    base = {"KEY": "original"}
    set_profile("dev", {"KEY": "overridden"}, profile_dir)
    apply_profile(base, "dev", profile_dir)
    assert base["KEY"] == "original"


def test_apply_profile_raises_for_missing(profile_dir):
    with pytest.raises(KeyError, match="Profile 'missing' not found"):
        apply_profile({}, "missing", profile_dir)
