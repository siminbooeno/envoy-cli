"""CLI commands for promoting .env values across environments."""

import argparse
from envoy.promote import promote_env_file


def cmd_promote(args: argparse.Namespace) -> None:
    keys = args.keys.split(",") if args.keys else None

    promoted = promote_env_file(
        source_path=args.source,
        target_path=args.target,
        keys=keys,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )

    if not promoted:
        print("Nothing to promote.")
        return

    if args.dry_run:
        print(f"[dry-run] Would promote {len(promoted)} key(s) to {args.target}:")
    else:
        print(f"Promoted {len(promoted)} key(s) to {args.target}:")

    for key in promoted:
        print(f"  + {key}")


def build_promote_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "promote",
        help="Promote env keys from one environment to another",
    )
    parser.add_argument("source", help="Source .env file path")
    parser.add_argument("target", help="Target .env file path")
    parser.add_argument(
        "--keys",
        default=None,
        help="Comma-separated list of keys to promote (default: all)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing keys in target",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing to disk",
    )
    parser.set_defaults(func=cmd_promote)
