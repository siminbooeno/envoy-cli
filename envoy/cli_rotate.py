"""CLI commands for key rotation."""

import argparse
from pathlib import Path

from envoy.rotate import rotate_env_file


def cmd_rotate(args: argparse.Namespace) -> None:
    env_path = Path(args.env_file)
    old_key_path = Path(args.old_key)
    new_key_path = Path(args.new_key)

    if not env_path.exists():
        print(f"[error] env file not found: {env_path}")
        return

    if not old_key_path.exists():
        print(f"[error] old key file not found: {old_key_path}")
        return

    if not new_key_path.exists():
        print(f"[error] new key file not found: {new_key_path}")
        return

    rotated = rotate_env_file(env_path, old_key_path, new_key_path)

    if not rotated:
        print("No encrypted secrets found — nothing rotated.")
        return

    print(f"Rotated {len(rotated)} secret(s) in {env_path}:")
    for key in rotated:
        print(f"  ~ {key}")


def build_rotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rotate",
        help="Re-encrypt secrets in an env file with a new vault key",
    )
    p.add_argument("env_file", help="Path to the .env file")
    p.add_argument("--old-key", required=True, help="Path to the current (old) key file")
    p.add_argument("--new-key", required=True, help="Path to the new key file")
    p.set_defaults(func=cmd_rotate)
