"""CLI commands for the trim feature."""

import argparse
from typing import Any

from envoy.trim import trim_env_file


def cmd_trim(args: Any) -> None:
    """Trim whitespace (and optionally quotes) from .env values."""
    import os

    if not os.path.exists(args.file):
        print(f"[error] File not found: {args.file}")
        return

    keys = args.keys if args.keys else None

    result = trim_env_file(
        args.file,
        keys=keys,
        strip_quotes=args.strip_quotes,
        dry_run=args.dry_run,
    )

    if result.total_trimmed == 0:
        print("Nothing to trim — all values are already clean.")
        return

    if args.dry_run:
        print(f"[dry-run] {result.total_trimmed} value(s) would be trimmed:")
    else:
        print(f"Trimmed {result.total_trimmed} value(s):")

    for key, new_val in result.trimmed.items():
        old_val = result.original.get(key, "")
        print(f"  {key}: {repr(old_val)} -> {repr(new_val)}")

    if not args.dry_run:
        print(f"\nSaved to {args.file}")


def build_trim_subparser(subparsers: Any) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "trim",
        help="Trim whitespace from .env values",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Only trim these specific keys (default: all keys)",
    )
    p.add_argument(
        "--strip-quotes",
        action="store_true",
        help="Also strip surrounding quote characters from values",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    p.set_defaults(func=cmd_trim)
    return p
