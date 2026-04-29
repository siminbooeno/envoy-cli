"""CLI interface for the normalize command."""

import argparse
import sys

from envoy.normalize import normalize_env_file


def cmd_normalize(args: argparse.Namespace) -> None:
    path = args.file
    try:
        result = normalize_env_file(
            path,
            keys=not args.no_keys,
            values=not args.no_values,
            lowercase_values=args.lowercase_values,
            only=args.only or None,
            dry_run=args.dry_run,
        )
    except FileNotFoundError:
        print(f"[error] file not found: {path}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"[dry-run] would normalize {result.total_changed} key(s) in {path}")
    else:
        print(f"Normalized {result.total_changed} key(s) in {path}")

    if args.verbose and result.changed:
        for key, old_val, new_val in result.changed:
            print(f"  {key}: {old_val!r} -> {new_val!r}")

    if result.total_skipped and args.verbose:
        print(f"  Skipped {result.total_skipped} key(s) (not in --only list)")


def build_normalize_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("normalize", help="Normalize keys and values in a .env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--no-keys", action="store_true", help="Skip key normalization")
    p.add_argument("--no-values", action="store_true", help="Skip value normalization")
    p.add_argument(
        "--lowercase-values", action="store_true", help="Lowercase all values"
    )
    p.add_argument(
        "--only", nargs="+", metavar="KEY", help="Only normalize specific keys"
    )
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("-v", "--verbose", action="store_true", help="Show changed keys")
    p.set_defaults(func=cmd_normalize)
