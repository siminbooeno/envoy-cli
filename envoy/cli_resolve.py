"""CLI commands for the resolve feature."""

import argparse
import sys
from typing import Optional

from envoy.parser import load_env_file, serialize_env
from envoy.resolve import resolve_env, unresolved_references, ResolutionError


def cmd_resolve(args: argparse.Namespace) -> None:
    """Resolve variable references in an .env file and print the result."""
    try:
        env = load_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        resolved = resolve_env(env, strict=args.strict)
    except ResolutionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    dangling = unresolved_references(resolved)
    if dangling and not args.quiet:
        for key, refs in dangling.items():
            print(
                f"  warning: '{key}' has unresolved reference(s): {', '.join(refs)}",
                file=sys.stderr,
            )

    if args.check:
        if dangling:
            print(
                f"Resolve check failed: {len(dangling)} unresolved reference(s).",
                file=sys.stderr,
            )
            sys.exit(1)
        print("All references resolved successfully.")
        return

    output = serialize_env(resolved)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
        print(f"Resolved env written to {args.output}")
    else:
        print(output, end="")


def build_resolve_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'resolve' sub-command."""
    p = subparsers.add_parser(
        "resolve",
        help="Expand variable references (${VAR}) within a .env file.",
    )
    p.add_argument("file", help="Path to the .env file to resolve.")
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Write resolved output to FILE instead of stdout.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any reference cannot be resolved.",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Only report whether all references resolve; do not print env.",
    )
    p.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress warnings about unresolved references.",
    )
    p.set_defaults(func=cmd_resolve)
