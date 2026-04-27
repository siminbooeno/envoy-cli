"""Tests for envoy.cli_diff_apply."""
from __future__ import annotations

import argparse
import sys

import pytest

from envoy.cli_diff_apply import build_diff_apply_subparser, cmd_diff_apply


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_file(tmp_path):
    f = tmp_path / "base.env"
    f.write_text("A=1\nB=2\n")
    return f


@pytest.fixture()
def source_file(tmp_path):
    f = tmp_path / "source.env"
    f.write_text("A=1\n")
    return f


@pytest.fixture()
def ref_file(tmp_path):
    f = tmp_path / "ref.env"
    f.write_text("A=1\nC=3\n")
    return f


def make_args(base, source, reference, **kwargs):
    defaults = dict(
        base=str(base),
        source=str(source),
        reference=str(reference),
        output=None,
        overwrite=False,
        keep_removed=False,
        dry_run=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_cmd_diff_apply_prints_summary(base_file, source_file, ref_file, capsys):
    args = make_args(base_file, source_file, ref_file)
    cmd_diff_apply(args)
    out = capsys.readouterr().out
    assert "Applied" in out
    assert "Skipped" in out


def test_cmd_diff_apply_verbose_shows_keys(base_file, source_file, ref_file, capsys):
    args = make_args(base_file, source_file, ref_file, verbose=True)
    cmd_diff_apply(args)
    out = capsys.readouterr().out
    assert "C" in out


def test_cmd_diff_apply_dry_run_prints_notice(base_file, source_file, ref_file, capsys):
    args = make_args(base_file, source_file, ref_file, dry_run=True)
    cmd_diff_apply(args)
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_cmd_diff_apply_missing_base_exits(tmp_path, source_file, ref_file):
    args = make_args(tmp_path / "missing.env", source_file, ref_file)
    with pytest.raises(SystemExit):
        cmd_diff_apply(args)


def test_cmd_diff_apply_output_path_used(base_file, source_file, ref_file, tmp_path, capsys):
    out_path = tmp_path / "out.env"
    args = make_args(base_file, source_file, ref_file, output=str(out_path))
    cmd_diff_apply(args)
    assert out_path.exists()
    out = capsys.readouterr().out
    assert str(out_path) in out


def test_build_diff_apply_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_diff_apply_subparser(subs)
    args = parser.parse_args(
        ["diff-apply", "base.env", "source.env", "ref.env"]
    )
    assert args.base == "base.env"
    assert args.source == "source.env"
    assert args.reference == "ref.env"
