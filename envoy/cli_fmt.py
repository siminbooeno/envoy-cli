"""CLI commands for formatting .env files."""

import argparse
import sys
from envoy.fmt import format_env_file


def cmd_fmt(args: argparse.Namespace) -> None:
    """Format an .env file in-place or preview changes."""
    path: str = args.file

    try:
        formatted, changed = format_env_file(
            path,
            sort=not args.no_sort,
            group=args.group,
            comment_groups=args.comment_groups,
            dry_run=args.dry_run or args.check,
        )
    except FileNotFoundError:
        print(f"[error] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    if args.check:
        if changed:
            print(f"[fmt] {path} would be reformatted")
            sys.exit(1)
        else:
            print(f"[fmt] {path} is already formatted")
        return

    if args.dry_run:
        print(formatted, end="")
        return

    if changed:
        print(f"[fmt] Reformatted {path}")
    else:
        print(f"[fmt] {path} is already formatted — no changes made")


def build_fmt_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "fmt",
        help="Format a .env file (sort keys, normalize style)",
    )
    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--no-sort",
        action="store_true",
        default=False,
        help="Do not sort keys alphabetically",
    )
    parser.add_argument(
        "--group",
        action="store_true",
        default=False,
        help="Group keys by prefix with blank lines between groups",
    )
    parser.add_argument(
        "--comment-groups",
        action="store_true",
        default=False,
        help="Add a comment header for each prefix group (requires --group)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the formatted output without writing to disk",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Exit with code 1 if the file would be reformatted (CI-friendly)",
    )
    parser.set_defaults(func=cmd_fmt)
