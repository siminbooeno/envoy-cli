"""CLI commands for env file history tracking."""

from __future__ import annotations

import argparse

from envoy.display import display_diff
from envoy.history import (
    clear_history,
    diff_history,
    load_history,
    record_snapshot,
)


def cmd_history_record(args: argparse.Namespace) -> None:
    entry = record_snapshot(args.env_file, label=args.label)
    ts = entry["timestamp"]
    label = f" [{entry['label']}]" if entry["label"] else ""
    print(f"Recorded snapshot at {ts}{label}")


def cmd_history_list(args: argparse.Namespace) -> None:
    entries = load_history(args.env_file)
    if not entries:
        print("No history found.")
        return
    for i, entry in enumerate(entries):
        label = f" | {entry['label']}" if entry["label"] else ""
        key_count = len(entry["data"])
        print(f"[{i}] {entry['timestamp']}{label} ({key_count} keys)")


def cmd_history_diff(args: argparse.Namespace) -> None:
    try:
        changes = diff_history(args.env_file, args.index_a, args.index_b)
    except IndexError as e:
        print(f"Error: {e}")
        return
    if not changes:
        print("No differences between the two snapshots.")
        return
    display_diff(changes, mask=not args.no_mask)


def cmd_history_clear(args: argparse.Namespace) -> None:
    clear_history(args.env_file)
    print(f"History cleared for {args.env_file}")


def build_history_subparser(subparsers) -> None:
    p = subparsers.add_parser("history", help="Manage env file change history")
    sub = p.add_subparsers(dest="history_cmd", required=True)

    rec = sub.add_parser("record", help="Record current state")
    rec.add_argument("env_file")
    rec.add_argument("--label", default="", help="Optional label for this snapshot")
    rec.set_defaults(func=cmd_history_record)

    lst = sub.add_parser("list", help="List recorded snapshots")
    lst.add_argument("env_file")
    lst.set_defaults(func=cmd_history_list)

    dif = sub.add_parser("diff", help="Diff two snapshots by index")
    dif.add_argument("env_file")
    dif.add_argument("index_a", type=int)
    dif.add_argument("index_b", type=int)
    dif.add_argument("--no-mask", action="store_true", help="Show secret values")
    dif.set_defaults(func=cmd_history_diff)

    clr = sub.add_parser("clear", help="Clear all history")
    clr.add_argument("env_file")
    clr.set_defaults(func=cmd_history_clear)
