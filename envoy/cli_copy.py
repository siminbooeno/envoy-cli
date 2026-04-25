"""CLI commands for copying keys between .env files."""

import argparse
from envoy.copy import copy_env_file


def cmd_copy(args: argparse.Namespace) -> None:
    source = args.source
    target = args.target
    keys = args.keys
    overwrite = args.overwrite
    dest = getattr(args, "output", None) or target
    dry_run = getattr(args, "dry_run", False)

    if dry_run:
        from envoy.parser import load_env_file
        source_env = load_env_file(source)
        target_env = load_env_file(target)
        from envoy.copy import copy_keys
        output, result = copy_keys(source_env, target_env, keys, overwrite=overwrite)
        if result.total_copied == 0 and result.total_missing == 0:
            print("Nothing to copy.")
        for k in result.copied:
            print(f"[dry-run] Would copy: {k}={output[k]}")
        for k in result.missing:
            print(f"[dry-run] Missing in source: {k}")
        for k in result.skipped:
            print(f"[dry-run] Would skip (exists): {k}")
        return

    result = copy_env_file(source, target, keys, overwrite=overwrite, dest_path=dest)

    for k in result.copied:
        print(f"Copied: {k}")
    for k in result.skipped:
        print(f"Skipped (exists): {k}")
    for k in result.missing:
        print(f"Missing in source: {k}")

    print(f"\nDone: {result.total_copied} copied, {result.total_skipped} skipped, {result.total_missing} missing.")


def build_copy_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("copy", help="Copy specific keys from one .env file to another")
    p.add_argument("source", help="Source .env file")
    p.add_argument("target", help="Target .env file")
    p.add_argument("keys", nargs="+", help="Keys to copy")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys in target")
    p.add_argument("--output", help="Write result to this file instead of modifying target")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_copy)
