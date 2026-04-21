"""CLI commands for managing env key groups."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.group import (
    add_to_group,
    delete_group,
    get_group_keys,
    list_groups,
    remove_from_group,
)


def cmd_group(args: argparse.Namespace) -> None:
    env_file = Path(args.file)

    if not env_file.exists():
        print(f"[error] File not found: {env_file}")
        return

    if args.group_action == "add":
        groups = add_to_group(env_file, args.group, args.keys)
        print(f"[group] Added {args.keys} to '{args.group}'")
        print(f"  keys: {groups[args.group]}")

    elif args.group_action == "remove":
        groups = remove_from_group(env_file, args.group, args.keys)
        remaining = groups.get(args.group, [])
        print(f"[group] Removed {args.keys} from '{args.group}'")
        if remaining:
            print(f"  remaining: {remaining}")
        else:
            print(f"  group '{args.group}' is now empty and was deleted")

    elif args.group_action == "delete":
        existed = delete_group(env_file, args.group)
        if existed:
            print(f"[group] Deleted group '{args.group}'")
        else:
            print(f"[group] Group '{args.group}' not found")

    elif args.group_action == "list":
        names = list_groups(env_file)
        if not names:
            print("[group] No groups defined")
        else:
            for name in names:
                keys = get_group_keys(env_file, name) or []
                print(f"  {name}: {', '.join(keys)}")

    elif args.group_action == "show":
        keys = get_group_keys(env_file, args.group)
        if keys is None:
            print(f"[group] Group '{args.group}' not found")
        else:
            print(f"[group] '{args.group}': {', '.join(keys) if keys else '(empty)'}")


def build_group_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("group", help="Manage named key groups in an env file")
    p.add_argument("file", help="Path to the .env file")
    sub = p.add_subparsers(dest="group_action", required=True)

    add_p = sub.add_parser("add", help="Add keys to a group")
    add_p.add_argument("group", help="Group name")
    add_p.add_argument("keys", nargs="+", help="Keys to add")

    rm_p = sub.add_parser("remove", help="Remove keys from a group")
    rm_p.add_argument("group", help="Group name")
    rm_p.add_argument("keys", nargs="+", help="Keys to remove")

    del_p = sub.add_parser("delete", help="Delete an entire group")
    del_p.add_argument("group", help="Group name")

    sub.add_parser("list", help="List all groups")

    show_p = sub.add_parser("show", help="Show keys in a group")
    show_p.add_argument("group", help="Group name")

    p.set_defaults(func=cmd_group)
