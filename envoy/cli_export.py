"""CLI commands for exporting .env files to various formats."""

import argparse
import sys

from envoy.export import export_env, EXPORT_FORMATS
from envoy.parser import load_env_file
from envoy.audit import log_event


def cmd_export(args: argparse.Namespace) -> None:
    """Handle the `envoy export` command."""
    try:
        env = load_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        result = export_env(
            env,
            fmt=args.format,
            masked=args.masked,
            output_path=args.output if hasattr(args, "output") else None,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    log_event(
        action="export",
        detail=f"file={args.file} format={args.format} masked={args.masked}",
    )

    if not (hasattr(args, "output") and args.output):
        print(result)
    else:
        print(f"Exported to {args.output}")


def build_export_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the export subcommand."""
    p = subparsers.add_parser("export", help="Export .env to shell, JSON, or Docker format")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--format",
        "-f",
        choices=EXPORT_FORMATS,
        default="shell",
        help="Output format (default: shell)",
    )
    p.add_argument(
        "--masked",
        action="store_true",
        default=False,
        help="Mask secret values in the output",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to this file instead of stdout",
    )
    p.set_defaults(func=cmd_export)
