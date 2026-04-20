"""Tests for envoy.snapshot module."""

import json
import pytest
from pathlib import Path

from envoy.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_NAME=envoy\nSECRET_KEY=supersecret\nDEBUG=true\n")
    return str(f), str(tmp_path)


def test_create_snapshot_creates_file(env_file):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, base_dir=base_dir)
    assert Path(snap_path).exists()


def test_create_snapshot_contains_correct_data(env_file):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, base_dir=base_dir)
    data = json.loads(Path(snap_path).read_text())
    assert data["data"]["APP_NAME"] == "envoy"
    assert data["data"]["SECRET_KEY"] == "supersecret"
    assert data["data"]["DEBUG"] == "true"


def test_create_snapshot_with_label(env_file):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, label="before-deploy", base_dir=base_dir)
    data = json.loads(Path(snap_path).read_text())
    assert data["label"] == "before-deploy"
    assert "before-deploy" in snap_path


def test_list_snapshots_returns_entries(env_file):
    env_path, base_dir = env_file
    create_snapshot(env_path, base_dir=base_dir)
    create_snapshot(env_path, label="v2", base_dir=base_dir)
    snaps = list_snapshots(env_path, base_dir=base_dir)
    assert len(snaps) == 2
    assert all("timestamp" in s for s in snaps)


def test_list_snapshots_empty_when_none_exist(env_file):
    env_path, base_dir = env_file
    snaps = list_snapshots(env_path, base_dir=base_dir)
    assert snaps == []


def test_restore_snapshot_overwrites_env(env_file, tmp_path):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, base_dir=base_dir)

    # Overwrite original
    Path(env_path).write_text("APP_NAME=changed\n")

    restored = restore_snapshot(snap_path, target_path=env_path)
    content = Path(restored).read_text()
    assert "APP_NAME=envoy" in content
    assert "SECRET_KEY=supersecret" in content


def test_restore_snapshot_to_new_path(env_file, tmp_path):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, base_dir=base_dir)
    new_target = str(tmp_path / ".env.restored")
    restore_snapshot(snap_path, target_path=new_target)
    assert Path(new_target).exists()


def test_delete_snapshot_removes_file(env_file):
    env_path, base_dir = env_file
    snap_path = create_snapshot(env_path, base_dir=base_dir)
    delete_snapshot(snap_path)
    assert not Path(snap_path).exists()


def test_delete_snapshot_raises_if_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_snapshot(str(tmp_path / "nonexistent.json"))
