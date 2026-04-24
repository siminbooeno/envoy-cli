"""CLI commands for the extract feature."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.extract import extract_env_file


def cmd_extract(args: argparse.Namespace) -> None:
    source = Path(args.source)
    if not source.exists():
        print(f"[error] Source file not found: {source}")
        return

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("[error] No keys specified.")
        return

    dest = Path(args.output) if args.output else None

    result = extract_env_file(
        source=source,
        keys=keys,
        dest=dest,
        overwrite=args.overwrite,
        ignore_missing=args.ignore_missing,
    )

    if result.missing:
        for k in result.missing:
            print(f"[missing] {k}")
        print(f"[error] {result.total_missing} key(s) not found in source.")
        return

    if args.dry_run or dest is None:
        for k, v in result.extracted.items():
            print(f"{k}={v}")
        if result.skipped:
            for k in result.skipped:
                print(f"[skipped] {k} (already exists in destination)")
        print(f"[dry-run] {result.total_extracted} key(s) would be extracted.")
        return

    for k in result.skipped:
        print(f"[skipped] {k} (already exists in destination)")
    print(f"[ok] Extracted {result.total_extracted} key(s) to {dest}")


def build_extract_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("extract", help="Extract specific keys into a new env file")
    p.add_argument("source", help="Source .env file")
    p.add_argument("keys", help="Comma-separated list of keys to extract")
    p.add_argument("-o", "--output", help="Destination .env file", default=None)
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys in destination")
    p.add_argument("--ignore-missing", action="store_true", help="Skip missing keys instead of erroring")
    p.add_argument("--dry-run", action="store_true", help="Preview extracted keys without writing")
    p.set_defaults(func=cmd_extract)
