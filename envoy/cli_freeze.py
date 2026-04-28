"""CLI commands for freeze/unfreeze of env keys."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.freeze import freeze_keys, unfreeze_keys, load_frozen


def cmd_freeze(args: argparse.Namespace) -> None:
    env_file = Path(args.file)
    if not env_file.exists():
        print(f"[error] File not found: {env_file}")
        return

    if args.action == "add":
        added = freeze_keys(env_file, args.keys)
        if added:
            for k in added:
                print(f"[frozen] {k}")
        else:
            print("[info] All specified keys were already frozen.")

    elif args.action == "remove":
        removed = unfreeze_keys(env_file, args.keys)
        if removed:
            for k in removed:
                print(f"[unfrozen] {k}")
        else:
            print("[info] None of the specified keys were frozen.")

    elif args.action == "list":
        frozen = load_frozen(env_file)
        if not frozen:
            print("[info] No keys are currently frozen.")
        else:
            print(f"Frozen keys in {env_file.name}:")
            for k in sorted(frozen):
                print(f"  - {k}")


def build_freeze_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "freeze", help="Freeze or unfreeze env keys to prevent modification."
    )
    parser.add_argument("file", help="Path to the .env file.")
    sub = parser.add_subparsers(dest="action", required=True)

    add_p = sub.add_parser("add", help="Freeze one or more keys.")
    add_p.add_argument("keys", nargs="+", help="Keys to freeze.")

    rem_p = sub.add_parser("remove", help="Unfreeze one or more keys.")
    rem_p.add_argument("keys", nargs="+", help="Keys to unfreeze.")

    sub.add_parser("list", help="List all frozen keys.")

    parser.set_defaults(func=cmd_freeze)
