"""CLI commands for the dedup feature."""

from __future__ import annotations

import argparse
import sys

from envoy.dedup import dedup_env_file


def cmd_dedup(args: argparse.Namespace) -> None:
    """Handle the `envoy dedup` subcommand."""
    try:
        result = dedup_env_file(
            path=args.file,
            keep=args.keep,
            dry_run=args.dry_run,
            output=getattr(args, "output", None),
        )
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.total_removed == 0:
        print("No duplicate keys found.")
        return

    print(f"Found {result.total_removed} duplicate(s) across {len(result.duplicates)} key(s):")
    for key, removed in result.duplicates.items():
        kept_value = result.kept[key]
        print(f"  {key}: kept={kept_value!r}, removed values: {[repr(v) for v in removed]}")

    if args.dry_run:
        print("(dry-run: no changes written)")
    else:
        dest = getattr(args, "output", None) or args.file
        print(f"Written to {dest}")


def build_dedup_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "dedup",
        help="Remove duplicate keys from a .env file",
    )
    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="last",
        help="Which occurrence to keep when a key is duplicated (default: last)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write result to a different file instead of overwriting the source",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without writing changes",
    )
    parser.set_defaults(func=cmd_dedup)
