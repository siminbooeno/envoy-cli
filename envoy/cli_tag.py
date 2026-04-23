"""CLI commands for tag management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envoy.tag import add_tag, remove_tag, get_tags, keys_with_tag, all_tags


def cmd_tag(args: argparse.Namespace) -> None:
    env_file = Path(args.file)

    if not env_file.exists():
        print(f"[error] File not found: {env_file}")
        return

    if args.tag_action == "add":
        add_tag(env_file, args.key, args.tag)
        print(f"[tag] Added '{args.tag}' to '{args.key}'")

    elif args.tag_action == "remove":
        remove_tag(env_file, args.key, args.tag)
        print(f"[tag] Removed '{args.tag}' from '{args.key}'")

    elif args.tag_action == "list":
        if args.key:
            tags = get_tags(env_file, args.key)
            if tags:
                print(f"{args.key}: {', '.join(tags)}")
            else:
                print(f"{args.key}: (no tags)")
        else:
            tag_set = all_tags(env_file)
            if tag_set:
                print("All tags: " + ", ".join(sorted(tag_set)))
            else:
                print("No tags defined.")

    elif args.tag_action == "filter":
        keys = keys_with_tag(env_file, args.tag)
        if keys:
            for k in keys:
                print(k)
        else:
            print(f"No keys tagged with '{args.tag}'")


def build_tag_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("tag", help="Manage tags on .env keys")
    parser.add_argument("file", help="Path to the .env file")
    sub = parser.add_subparsers(dest="tag_action", required=True)

    add_p = sub.add_parser("add", help="Add a tag to a key")
    add_p.add_argument("key", help="Key name")
    add_p.add_argument("tag", help="Tag to add")

    rem_p = sub.add_parser("remove", help="Remove a tag from a key")
    rem_p.add_argument("key", help="Key name")
    rem_p.add_argument("tag", help="Tag to remove")

    lst_p = sub.add_parser("list", help="List tags")
    lst_p.add_argument("--key", default=None, help="Specific key to list tags for")

    flt_p = sub.add_parser("filter", help="List keys with a given tag")
    flt_p.add_argument("tag", help="Tag to filter by")

    parser.set_defaults(func=cmd_tag)
