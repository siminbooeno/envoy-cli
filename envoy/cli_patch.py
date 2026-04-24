"""CLI sub-commands for the patch feature."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from envoy.patch import patch_env_file


def cmd_patch(args: argparse.Namespace) -> None:
    """Entry-point for `envoy patch`."""
    if not args.set and not args.remove:
        print("error: provide at least one --set KEY=VALUE or --remove KEY", file=sys.stderr)
        sys.exit(1)

    updates: dict[str, Optional[str]] = {}

    for item in args.set or []:
        if "=" not in item:
            print(f"error: --set value must be KEY=VALUE, got: {item!r}", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        updates[k.strip()] = v

    for key in args.remove or []:
        updates[key.strip()] = None

    try:
        report = patch_env_file(
            args.file,
            updates,
            overwrite=not args.no_overwrite,
            remove_nulls=True,
            dry_run=args.dry_run,
        )
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("[dry-run] no changes written")

    for key in report.added:
        print(f"  + {key}")
    for key in report.updated:
        print(f"  ~ {key}")
    for key in report.removed:
        print(f"  - {key}")
    for key in report.skipped:
        print(f"  = {key} (skipped)")

    if report.total_changed == 0 and not report.skipped:
        print("nothing to patch")


def build_patch_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("patch", help="Apply key-value patches to an env file")
    p.add_argument("file", help="Target .env file")
    p.add_argument("--set", metavar="KEY=VALUE", action="append", help="Set a key")
    p.add_argument("--remove", metavar="KEY", action="append", help="Remove a key")
    p.add_argument("--no-overwrite", action="store_true", help="Skip existing keys")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_patch)
