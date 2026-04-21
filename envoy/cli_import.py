"""CLI commands for importing environment variables from various sources."""

import argparse
import json
import os
import sys
from pathlib import Path

from envoy.import_env import import_from_os, import_from_json, import_from_dotenv_string, merge_imported
from envoy.parser import load_env_file, serialize_env
from envoy.audit import log_event


def cmd_import(args: argparse.Namespace) -> None:
    """Import environment variables into a target .env file.

    Supports importing from:
      - The current OS environment (--from-os)
      - A JSON file (--from-json)
      - A raw dotenv-formatted string via stdin (--from-stdin)
    """
    target_path = Path(args.target)

    # Load existing target env if it exists
    existing: dict[str, str] = {}
    if target_path.exists():
        existing = load_env_file(str(target_path))

    imported: dict[str, str] = {}

    if args.from_os:
        prefix = args.prefix or ""
        imported = import_from_os(prefix=prefix)
        source_label = f"OS environment (prefix={prefix!r})"

    elif args.from_json:
        json_path = Path(args.from_json)
        if not json_path.exists():
            print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
            sys.exit(1)
        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid JSON — {exc}", file=sys.stderr)
            sys.exit(1)
        imported = import_from_json(raw)
        source_label = f"JSON file ({json_path})"

    elif args.from_stdin:
        dotenv_string = sys.stdin.read()
        imported = import_from_dotenv_string(dotenv_string)
        source_label = "stdin (dotenv format)"

    else:
        print("Error: specify one of --from-os, --from-json, or --from-stdin.", file=sys.stderr)
        sys.exit(1)

    if not imported:
        print("No variables imported.")
        return

    merged = merge_imported(
        base=existing,
        incoming=imported,
        overwrite=args.overwrite,
    )

    added = [k for k in imported if k not in existing]
    updated = [k for k in imported if k in existing and existing[k] != imported[k] and args.overwrite]
    skipped = [k for k in imported if k in existing and not args.overwrite]

    if args.dry_run:
        print(f"[dry-run] Would write {len(merged)} keys to {target_path}")
        print(f"  + added:   {len(added)}")
        print(f"  ~ updated: {len(updated)}")
        print(f"  - skipped: {len(skipped)}")
        return

    target_path.write_text(serialize_env(merged), encoding="utf-8")

    log_event(
        action="import",
        target=str(target_path),
        detail=(
            f"source={source_label}, "
            f"added={len(added)}, updated={len(updated)}, skipped={len(skipped)}"
        ),
        env_dir=str(target_path.parent),
    )

    print(f"Imported into {target_path}:")
    print(f"  + added:   {len(added)}")
    print(f"  ~ updated: {len(updated)}")
    print(f"  - skipped: {len(skipped)} (use --overwrite to replace)")


def build_import_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'import' subcommand with the main CLI parser."""
    parser = subparsers.add_parser(
        "import",
        help="Import environment variables from OS, JSON, or stdin into a .env file.",
    )
    parser.add_argument(
        "target",
        help="Path to the target .env file to write into.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--from-os",
        action="store_true",
        help="Import from the current OS environment.",
    )
    source_group.add_argument(
        "--from-json",
        metavar="FILE",
        help="Import from a flat JSON file.",
    )
    source_group.add_argument(
        "--from-stdin",
        action="store_true",
        help="Import from a dotenv-formatted string on stdin.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Filter OS env vars by prefix (stripped from key names). Only used with --from-os.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing keys in the target file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk.",
    )
    parser.set_defaults(func=cmd_import)
