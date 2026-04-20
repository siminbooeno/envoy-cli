"""CLI commands for linting .env files."""

import argparse
import sys

from envoy.lint import lint_env_file, Severity
from envoy.audit import log_event


def cmd_lint(args: argparse.Namespace) -> None:
    """Run lint checks on a .env file and report issues."""
    try:
        result = lint_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not result.issues:
        print(f"✔ No issues found in {args.file}")
        log_event("lint", args.file, {"status": "clean"})
        return

    for issue in result.issues:
        icon = "✖" if issue.severity == Severity.ERROR else "⚠"
        print(f"  {icon} {issue}")

    print(f"\n{result.summary()}")

    log_event("lint", args.file, {
        "errors": sum(1 for i in result.issues if i.severity == Severity.ERROR),
        "warnings": sum(1 for i in result.issues if i.severity == Severity.WARNING),
    })

    if args.strict and result.has_errors:
        sys.exit(1)


def build_lint_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the lint subcommand."""
    p = subparsers.add_parser("lint", help="Lint a .env file for common issues")
    p.add_argument("file", help="Path to the .env file to lint")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if errors are found",
    )
    p.set_defaults(func=cmd_lint)
