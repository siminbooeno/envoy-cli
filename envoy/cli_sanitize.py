"""CLI commands for the sanitize feature."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.parser import load_env_file, serialize_env
from envoy.sanitize import sanitize_env


def cmd_sanitize(args: argparse.Namespace) -> None:
    src = Path(args.file)
    if not src.exists():
        print(f"[error] file not found: {src}")
        return

    env = load_env_file(str(src))
    keys = args.keys if args.keys else None

    result = sanitize_env(
        env,
        keys=keys,
        strip_whitespace=not args.no_strip,
        remove_control_chars=not args.no_control,
        collapse_newlines=not args.no_newlines,
        newline_replacement=args.newline_replacement,
        max_length=args.max_length,
    )

    if args.dry_run:
        if not result.changes:
            print("No changes needed.")
        else:
            print(f"Would sanitize {result.total_changed} value(s):")
            for k, (orig, clean) in result.changes.items():
                print(f"  {k}: {repr(orig)} -> {repr(clean)}")
        if result.skipped:
            print(f"Skipped (not found): {', '.join(result.skipped)}")
        return

    dest = Path(args.output) if args.output else src
    dest.write_text(serialize_env(result.sanitized))

    if result.total_changed == 0:
        print("No changes needed.")
    else:
        print(f"Sanitized {result.total_changed} value(s) in {dest}")
        if args.verbose:
            for k, (orig, clean) in result.changes.items():
                print(f"  {k}: {repr(orig)} -> {repr(clean)}")

    if result.skipped:
        print(f"Skipped (not found): {', '.join(result.skipped)}")


def build_sanitize_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("sanitize", help="Sanitize .env values")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Only sanitize these keys")
    p.add_argument("--output", "-o", help="Write result to this file (default: in-place)")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("--verbose", "-v", action="store_true", help="Show each change")
    p.add_argument("--no-strip", action="store_true", help="Disable whitespace stripping")
    p.add_argument("--no-control", action="store_true", help="Disable control-char removal")
    p.add_argument("--no-newlines", action="store_true", help="Disable newline collapsing")
    p.add_argument("--newline-replacement", default=" ", metavar="STR",
                   help="Replacement for collapsed newlines (default: space)")
    p.add_argument("--max-length", type=int, default=None, metavar="N",
                   help="Truncate values longer than N characters")
    p.set_defaults(func=cmd_sanitize)
