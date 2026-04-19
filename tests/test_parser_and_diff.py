"""Tests for env parser, diff engine, and masking."""

import pytest
from envoy.parser import parse_env_file, serialize_env
from envoy.diff import compute_diff, ChangeType
from envoy.masking import is_secret, mask_env, get_secret_keys


ENV_SAMPLE = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD="super secret"
API_KEY=abc123
APP_NAME=myapp
"""


def test_parse_basic():
    data = parse_env_file(ENV_SAMPLE)
    assert data['DB_HOST'] == 'localhost'
    assert data['DB_PORT'] == '5432'
    assert data['DB_PASSWORD'] == 'super secret'
    assert data['API_KEY'] == 'abc123'
    assert data['APP_NAME'] == 'myapp'


def test_parse_ignores_comments():
    data = parse_env_file(ENV_SAMPLE)
    assert '# Database config' not in data


def test_serialize_roundtrip():
    data = {'FOO': 'bar', 'BAZ': 'hello world'}
    serialized = serialize_env(data)
    reparsed = parse_env_file(serialized)
    assert reparsed['FOO'] == 'bar'
    assert reparsed['BAZ'] == 'hello world'


def test_diff_added():
    base = {'A': '1'}
    target = {'A': '1', 'B': '2'}
    diffs = {d.key: d for d in compute_diff(base, target)}
    assert diffs['B'].change == ChangeType.ADDED


def test_diff_removed():
    base = {'A': '1', 'B': '2'}
    target = {'A': '1'}
    diffs = {d.key: d for d in compute_diff(base, target)}
    assert diffs['B'].change == ChangeType.REMOVED


def test_diff_modified():
    base = {'A': '1'}
    target = {'A': '2'}
    diffs = {d.key: d for d in compute_diff(base, target)}
    assert diffs['A'].change == ChangeType.MODIFIED


def test_is_secret():
    assert is_secret('DB_PASSWORD')
    assert is_secret('API_KEY')
    assert is_secret('MY_SECRET_VALUE')
    assert not is_secret('APP_NAME')
    assert not is_secret('DB_HOST')


def test_mask_env():
    data = parse_env_file(ENV_SAMPLE)
    masked = mask_env(data)
    assert masked['DB_PASSWORD'] == '********'
    assert masked['API_KEY'] == '********'
    assert masked['APP_NAME'] == 'myapp'


def test_get_secret_keys():
    data = parse_env_file(ENV_SAMPLE)
    secrets = get_secret_keys(data)
    assert 'DB_PASSWORD' in secrets
    assert 'API_KEY' in secrets
    assert 'APP_NAME' not in secrets
