"""CLI commands for comparing .env files."""

import argparse
import sys

from envoy.compare import compare_env_files, format_report
from envoy.audit import log_event


def cmd_compare(args: argparse.Namespace) -> None:
    """Handle the 'compare' CLI command."""
    try:
        report = compare_env_files(
            source_path=args.source,
            target_path=args.target,
            mask_secrets=args.mask,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = format_report(report, verbose=args.verbose)
    print(output)

    log_event(
        action="compare",
        detail={
            "source": args.source,
            "target": args.target,
            "added": len(report.source_only),
            "removed": len(report.target_only),
            "changed": len(report.changed),
        },
    )

    if args.exit_code and report.has_differences:
        sys.exit(1)


def build_compare_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'compare' subcommand."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two .env files and show differences",
    )
    parser.add_argument("source", help="Source .env file (reference)")
    parser.add_argument("target", help="Target .env file to compare against")
    parser.add_argument(
        "--mask",
        action="store_true",
        default=False,
        help="Mask secret values in output",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Show per-key diff details",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        dest="exit_code",
        help="Exit with code 1 if differences are found (useful in CI)",
    )
    parser.set_defaults(func=cmd_compare)
