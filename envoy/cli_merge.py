"""CLI commands for merging multiple .env files."""

import argparse
import sys
from envoy.merge import merge_env_files, MergeStrategy, MergeConflict
from envoy.parser import serialize_env


def cmd_merge(args: argparse.Namespace) -> None:
    strategy = MergeStrategy(args.strategy)

    try:
        merged = merge_env_files(
            paths=args.files,
            output_path=args.output if not args.dry_run else None,
            strategy=strategy,
        )
    except MergeConflict as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run or args.verbose:
        print(serialize_env(merged))

    if not args.dry_run and args.output:
        print(f"[merged] {len(merged)} keys written to {args.output}")
    elif not args.dry_run and not args.output:
        # No output file — print to stdout
        print(serialize_env(merged))


def build_merge_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "merge",
        help="Merge multiple .env files into one",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to merge (in order)",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        default=None,
        help="Write merged result to this file",
    )
    parser.add_argument(
        "--strategy",
        choices=[s.value for s in MergeStrategy],
        default=MergeStrategy.LAST.value,
        help="Conflict resolution strategy (default: last)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview merged output without writing",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print merged content even when writing to a file",
    )
    parser.set_defaults(func=cmd_merge)
