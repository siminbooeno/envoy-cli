"""CLI commands for searching .env files."""
from __future__ import annotations

import argparse
import sys

from envoy.masking import mask_value, is_secret
from envoy.search import search_env_file, SearchReport


def _print_report(report: SearchReport, *, masked: bool, verbose: bool) -> None:
    if report.total == 0:
        print(f"No matches found for '{report.pattern}'.")
        return

    print(f"Found {report.total} match(es) for '{report.pattern}':")
    for result in report.results:
        display_value = mask_value(result.value) if masked and is_secret(result.key) else result.value
        if verbose:
            flags = []
            if result.matched_key:
                flags.append("key")
            if result.matched_value:
                flags.append("value")
            print(f"  {result.key}={display_value}  [{', '.join(flags)}]")
        else:
            print(f"  {result.key}={display_value}")


def cmd_search(args: argparse.Namespace) -> None:
    try:
        report = search_env_file(
            args.file,
            args.pattern,
            search_keys=not args.values_only,
            search_values=not args.keys_only,
            case_sensitive=args.case_sensitive,
            exact=args.exact,
        )
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    _print_report(report, masked=args.masked, verbose=args.verbose)

    if args.fail_on_no_match and report.total == 0:
        sys.exit(2)


def build_search_subparser(subparsers) -> None:
    p = subparsers.add_parser("search", help="Search keys/values in a .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("pattern", help="Pattern to search for")
    p.add_argument("--keys-only", action="store_true", help="Only search key names")
    p.add_argument("--values-only", action="store_true", help="Only search values")
    p.add_argument("--case-sensitive", action="store_true", help="Case-sensitive match")
    p.add_argument("--exact", action="store_true", help="Require exact match")
    p.add_argument("--masked", action="store_true", help="Mask secret values in output")
    p.add_argument("--verbose", action="store_true", help="Show which field matched")
    p.add_argument("--fail-on-no-match", action="store_true", help="Exit with code 2 if no matches")
    p.set_defaults(func=cmd_search)
