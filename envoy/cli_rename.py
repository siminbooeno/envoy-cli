"""CLI commands for renaming keys in .env files."""

import argparse
from pathlib import Path
from envoy.rename import rename_env_file, rename_across_files


def cmd_rename(args: argparse.Namespace) -> None:
    paths = [Path(p) for p in args.files]

    if not paths:
        print("No files specified.")
        return

    if args.dry_run:
        print(f"[dry-run] Would rename '{args.old_key}' -> '{args.new_key}'")

    if len(paths) == 1:
        result = rename_env_file(
            paths[0],
            args.old_key,
            args.new_key,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        _print_result(paths[0], result, args.old_key, args.new_key)
    else:
        results = rename_across_files(
            paths,
            args.old_key,
            args.new_key,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        for path, result in results.items():
            _print_result(path, result, args.old_key, args.new_key)


def _print_result(path, result, old_key, new_key) -> None:
    if result.renamed:
        print(f"  [{path}] Renamed '{old_key}' -> '{new_key}'")
    elif result.skipped:
        print(f"  [{path}] Key '{old_key}' not found — skipped")
    elif result.conflicts:
        print(
            f"  [{path}] Key '{new_key}' already exists — use --overwrite to replace"
        )


def build_rename_subparser(subparsers) -> None:
    parser = subparsers.add_parser("rename", help="Rename a key in one or more .env files")
    parser.add_argument("old_key", help="Existing key name")
    parser.add_argument("new_key", help="New key name")
    parser.add_argument("files", nargs="+", help="Target .env file(s)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite new_key if it already exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    parser.set_defaults(func=cmd_rename)
