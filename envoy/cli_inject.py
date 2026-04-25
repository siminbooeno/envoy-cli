"""CLI commands for the inject feature."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envoy.inject import inject_env, inject_and_run
from envoy.parser import load_env_file


def cmd_inject(args: argparse.Namespace) -> None:
    """Inject env file values into a subprocess command."""
    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        sys.exit(1)

    keys: List[str] | None = args.keys if args.keys else None

    if not args.command:
        # Dry-run: just show what would be injected
        base = {}
        result = inject_env(env, base=base, overwrite=args.overwrite, keys=keys)
        if not result.injected:
            print("Nothing to inject.")
            return
        print(f"Would inject {result.total_injected} key(s):")
        for k in result.injected:
            print(f"  {k}")
        return

    result = inject_and_run(
        args.env_file,
        args.command,
        overwrite=args.overwrite,
        keys=keys,
    )

    if args.verbose:
        print(f"Injected {result.total_injected} key(s), "
              f"skipped {len(result.skipped)}.")
    sys.exit(result.returncode or 0)


def build_inject_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "inject",
        help="Inject .env variables into a subprocess command.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run with injected environment.",
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Only inject these keys.",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing env vars (default: True).",
    )
    p.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="Do not overwrite existing env vars.",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_inject)
