"""Main CLI entry point for envoy."""

from __future__ import annotations

import argparse
import sys

from envoy.parser import load_env_file, serialize_env
from envoy.diff import compute_diff
from envoy.display import display_diff
from envoy.masking import mask_env
from envoy.sync import sync_env
from envoy.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envoy.cli_audit import build_audit_subparser
from envoy.cli_export import build_export_subparser
from envoy.cli_lint import build_lint_subparser
from envoy.cli_compare import build_compare_subparser
from envoy.cli_watch import build_watch_subparser
from envoy.cli_history import build_history_subparser
from envoy.cli_rotate import build_rotate_subparser
from envoy.cli_import import build_import_subparser
from envoy.cli_promote import build_promote_subparser
from envoy.cli_pin import build_pin_subparser
from envoy.cli_resolve import build_resolve_subparser
from envoy.cli_rename import build_rename_subparser
from envoy.cli_clone import build_clone_subparser


def cmd_diff(args: argparse.Namespace) -> None:
    source = load_env_file(args.source)
    target = load_env_file(args.target)
    diff = compute_diff(source, target)
    display_diff(diff, masked=args.masked)


def cmd_sync(args: argparse.Namespace) -> None:
    result = sync_env(args.source, args.target, overwrite=args.overwrite)
    print(f"Synced {len(result.added)} added, {len(result.updated)} updated, {len(result.skipped)} skipped.")


def cmd_mask(args: argparse.Namespace) -> None:
    env = load_env_file(args.file)
    masked = mask_env(env)
    print(serialize_env(masked))


def cmd_snapshot(args: argparse.Namespace) -> None:
    if args.snapshot_cmd == "create":
        snap = create_snapshot(args.file, label=args.label)
        print(f"Snapshot created: {snap['id']}")
    elif args.snapshot_cmd == "list":
        snaps = list_snapshots(args.file)
        if not snaps:
            print("No snapshots found.")
        for s in snaps:
            label = f" ({s['label']})" if s.get("label") else ""
            print(f"  {s['id']}{label} — {s['timestamp']}")
    elif args.snapshot_cmd == "restore":
        restore_snapshot(args.file, args.snapshot_id)
        print(f"Restored snapshot {args.snapshot_id} to {args.file}")
    elif args.snapshot_cmd == "delete":
        delete_snapshot(args.file, args.snapshot_id)
        print(f"Deleted snapshot {args.snapshot_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="envoy", description="Manage .env files")
    subparsers = parser.add_subparsers(dest="command")

    diff_p = subparsers.add_parser("diff", help="Show diff between two .env files")
    diff_p.add_argument("source")
    diff_p.add_argument("target")
    diff_p.add_argument("--masked", action="store_true")
    diff_p.set_defaults(func=cmd_diff)

    sync_p = subparsers.add_parser("sync", help="Sync keys from source to target")
    sync_p.add_argument("source")
    sync_p.add_argument("target")
    sync_p.add_argument("--overwrite", action="store_true")
    sync_p.set_defaults(func=cmd_sync)

    mask_p = subparsers.add_parser("mask", help="Print .env with secrets masked")
    mask_p.add_argument("file")
    mask_p.set_defaults(func=cmd_mask)

    snap_p = subparsers.add_parser("snapshot", help="Manage .env snapshots")
    snap_sub = snap_p.add_subparsers(dest="snapshot_cmd")
    sc = snap_sub.add_parser("create")
    sc.add_argument("file")
    sc.add_argument("--label", default=None)
    sl = snap_sub.add_parser("list")
    sl.add_argument("file")
    sr = snap_sub.add_parser("restore")
    sr.add_argument("file")
    sr.add_argument("snapshot_id")
    sd = snap_sub.add_parser("delete")
    sd.add_argument("file")
    sd.add_argument("snapshot_id")
    snap_p.set_defaults(func=cmd_snapshot)

    build_audit_subparser(subparsers)
    build_export_subparser(subparsers)
    build_lint_subparser(subparsers)
    build_compare_subparser(subparsers)
    build_watch_subparser(subparsers)
    build_history_subparser(subparsers)
    build_rotate_subparser(subparsers)
    build_import_subparser(subparsers)
    build_promote_subparser(subparsers)
    build_pin_subparser(subparsers)
    build_resolve_subparser(subparsers)
    build_rename_subparser(subparsers)
    build_clone_subparser(subparsers)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
