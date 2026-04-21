"""CLI commands for managing env key pins."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy.parser import load_env_file
from envoy.pin import add_pin, remove_pin, check_pins, list_pins


def cmd_pin(args: argparse.Namespace) -> None:
    directory = str(Path(args.env_file).parent) if hasattr(args, "env_file") else "."

    if args.pin_action == "add":
        pins = add_pin(args.key, args.value, directory=directory)
        print(f"Pinned {args.key}={args.value}")
        print(f"Total pins: {len(pins)}")

    elif args.pin_action == "remove":
        removed = remove_pin(args.key, directory=directory)
        if removed:
            print(f"Removed pin for '{args.key}'")
        else:
            print(f"No pin found for '{args.key}'")
            sys.exit(1)

    elif args.pin_action == "list":
        pins = list_pins(directory=directory)
        if not pins:
            print("No pins defined.")
        else:
            for key, value in sorted(pins.items()):
                print(f"  {key}={value}")

    elif args.pin_action == "check":
        env = load_env_file(args.env_file)
        violations = check_pins(env, directory=directory)
        if not violations:
            print("All pinned keys match. ✓")
        else:
            print(f"Pin violations ({len(violations)}):")
            for v in violations:
                print(f"  ✗ {v}")
            sys.exit(1)


def build_pin_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("pin", help="Lock env keys to specific values")
    p.add_argument("env_file", help="Path to the .env file")
    sub = p.add_subparsers(dest="pin_action", required=True)

    add_p = sub.add_parser("add", help="Pin a key to a value")
    add_p.add_argument("key", help="Key to pin")
    add_p.add_argument("value", help="Expected value")

    rm_p = sub.add_parser("remove", help="Remove a pin")
    rm_p.add_argument("key", help="Key to unpin")

    sub.add_parser("list", help="List all pins")
    sub.add_parser("check", help="Validate env file against pins")

    p.set_defaults(func=cmd_pin)
