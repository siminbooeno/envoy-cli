"""CLI commands for cloning .env files."""

from __future__ import annotations

import argparse

from envoy.clone import clone_env


def cmd_clone(args: argparse.Namespace) -> None:
    include = args.include.split(",") if args.include else None
    exclude = args.exclude.split(",") if args.exclude else None

    try:
        result = clone_env(
            source=args.source,
            destination=args.destination,
            include_keys=include,
            exclude_keys=exclude,
            masked=args.masked,
            overwrite=args.overwrite,
        )
    except FileNotFoundError as e:
        print(f"[error] {e}")
        return
    except FileExistsError as e:
        print(f"[error] {e}")
        return

    print(f"Cloned '{result.source}' → '{result.destination}'")
    print(f"  Copied : {result.total_copied} key(s)")
    if result.total_skipped:
        print(f"  Skipped: {result.total_skipped} key(s)")
    if args.verbose and result.keys_copied:
        print("  Keys copied:")
        for k in result.keys_copied:
            print(f"    + {k}")
    if args.verbose and result.keys_skipped:
        print("  Keys skipped:")
        for k in result.keys_skipped:
            print(f"    - {k}")


def build_clone_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("clone", help="Clone a .env file to a new location")
    p.add_argument("source", help="Source .env file")
    p.add_argument("destination", help="Destination .env file")
    p.add_argument("--include", default=None, help="Comma-separated list of keys to include")
    p.add_argument("--exclude", default=None, help="Comma-separated list of keys to exclude")
    p.add_argument("--masked", action="store_true", help="Mask secret values in the clone")
    p.add_argument("--overwrite", action="store_true", help="Overwrite destination if it exists")
    p.add_argument("--verbose", action="store_true", help="Show individual key details")
    p.set_defaults(func=cmd_clone)
