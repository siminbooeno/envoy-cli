"""CLI commands for managing env key aliases."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.alias import add_alias, remove_alias, list_aliases, resolve_alias


def cmd_alias(args: argparse.Namespace) -> None:
    env_file = Path(args.file)

    if not env_file.exists():
        print(f"[error] File not found: {env_file}")
        return

    if args.alias_action == "add":
        add_alias(env_file, args.alias, args.original)
        print(f"[alias] '{args.alias}' -> '{args.original}' added.")

    elif args.alias_action == "remove":
        removed = remove_alias(env_file, args.alias)
        if removed:
            print(f"[alias] '{args.alias}' removed.")
        else:
            print(f"[alias] '{args.alias}' not found.")

    elif args.alias_action == "resolve":
        original = resolve_alias(env_file, args.alias)
        if original:
            print(f"{args.alias} -> {original}")
        else:
            print(f"[alias] '{args.alias}' not found.")

    elif args.alias_action == "list":
        entries = list_aliases(env_file)
        if not entries:
            print("[alias] No aliases defined.")
        else:
            for entry in entries:
                print(f"  {entry['alias']} -> {entry['original']}")


def build_alias_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("alias", help="Manage key aliases for an env file")
    p.add_argument("file", help="Path to the .env file")
    sub = p.add_subparsers(dest="alias_action", required=True)

    add_p = sub.add_parser("add", help="Add an alias")
    add_p.add_argument("alias", help="Alias name")
    add_p.add_argument("original", help="Original key name")

    rm_p = sub.add_parser("remove", help="Remove an alias")
    rm_p.add_argument("alias", help="Alias name to remove")

    res_p = sub.add_parser("resolve", help="Resolve an alias to its original key")
    res_p.add_argument("alias", help="Alias name to resolve")

    sub.add_parser("list", help="List all aliases")

    p.set_defaults(func=cmd_alias)
