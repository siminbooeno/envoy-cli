"""CLI commands for applying diffs between env files."""
from __future__ import annotations

import argparse
import sys

from envoy.diff_apply import apply_diff_files


def cmd_diff_apply(args: argparse.Namespace) -> None:
    """Apply the diff between SOURCE and REFERENCE onto BASE."""
    try:
        result = apply_diff_files(
            base_path=args.base,
            source_path=args.source,
            reference_path=args.reference,
            output_path=args.output,
            overwrite=args.overwrite,
            remove_deleted=not args.keep_removed,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    dest = args.output or args.base

    if args.dry_run:
        print("[dry-run] No files were written.")

    print(f"Applied  : {result.total_applied} key(s)")
    print(f"Skipped  : {result.total_skipped} key(s)")
    print(f"Removed  : {len(result.removed)} key(s)")

    if result.has_conflicts:
        print(f"Conflicts: {len(result.conflicts)} key(s)")
        for key in result.conflicts:
            print(f"  ! {key}")

    if args.verbose:
        for key in result.applied:
            print(f"  + {key}")
        for key in result.removed:
            print(f"  - {key}")
        for key in result.skipped:
            print(f"  ~ {key} (skipped)")

    if not args.dry_run:
        print(f"Output written to: {dest}")


def build_diff_apply_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "diff-apply",
        help="Apply the diff between two env files onto a base file",
    )
    p.add_argument("base", help="Base .env file to patch")
    p.add_argument("source", help="Source env (diff computed FROM this)")
    p.add_argument("reference", help="Reference env (diff computed TO this)")
    p.add_argument("-o", "--output", default=None, help="Output path (default: overwrite base)")
    p.add_argument("--overwrite", action="store_true", help="Overwrite conflicting keys")
    p.add_argument("--keep-removed", action="store_true", help="Do not remove keys deleted in diff")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("-v", "--verbose", action="store_true", help="Show individual key changes")
    p.set_defaults(func=cmd_diff_apply)
