"""CLI commands for filtering env file entries."""
from __future__ import annotations

import argparse
import sys

from envoy.parser import load_env_file, serialize_env
from envoy.filter import filter_env
from envoy.masking import mask_env


def cmd_filter(args: argparse.Namespace) -> None:
    try:
        env = load_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = filter_env(
        env,
        prefix=args.prefix,
        pattern=args.pattern,
        value_pattern=args.value_pattern,
        exclude_empty=args.exclude_empty,
    )

    display = result.matched
    if args.masked:
        display = mask_env(display)

    if args.output:
        with open(args.output, "w") as f:
            f.write(serialize_env(display))
        print(f"Wrote {result.total_matched} key(s) to {args.output}")
        if args.verbose:
            print(f"Excluded {result.total_excluded} key(s)")
    else:
        if not display:
            print("No keys matched the given filters.")
        else:
            for k, v in display.items():
                print(f"{k}={v}")
        if args.verbose:
            print(f"\n({result.total_matched} matched, {result.total_excluded} excluded)")


def build_filter_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("filter", help="Filter env file entries by key/value criteria")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--prefix", default=None, help="Keep only keys with this prefix")
    p.add_argument("--pattern", default=None, help="Keep only keys matching this regex")
    p.add_argument("--value-pattern", dest="value_pattern", default=None,
                   help="Keep only entries whose value matches this regex")
    p.add_argument("--exclude-empty", action="store_true",
                   help="Exclude entries with empty values")
    p.add_argument("--output", "-o", default=None, help="Write filtered result to this file")
    p.add_argument("--masked", action="store_true", help="Mask secret values in output")
    p.add_argument("--verbose", "-v", action="store_true", help="Show match/exclude counts")
    p.set_defaults(func=cmd_filter)
