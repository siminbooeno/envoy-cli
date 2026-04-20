"""Main CLI entry point for envoy-cli.

Provides subcommands for diffing, syncing, masking, snapshotting,
and vault operations on .env files.
"""

import argparse
import sys
from pathlib import Path

from envoy.parser import load_env_file, serialize_env
from envoy.diff import compute_diff, has_changes
from envoy.display import display_diff
from envoy.masking import mask_env
from envoy.sync import sync_env
from envoy.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envoy.cli_vault import cmd_keygen, cmd_encrypt, cmd_decrypt


def cmd_diff(args: argparse.Namespace) -> int:
    """Show diff between two .env files."""
    source = load_env_file(args.source)
    target = load_env_file(args.target)
    diff = compute_diff(source, target)

    display_diff(diff, mask_secrets=not args.show_secrets)

    return 0 if not has_changes(diff) else 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync keys from source .env into target .env."""
    added, skipped = sync_env(
        source_path=args.source,
        target_path=args.target,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("[dry-run] No changes written.")

    print(f"Added: {len(added)}  Skipped: {len(skipped)}")
    if added:
        print("  Added keys:  ", ", ".join(added))
    if skipped:
        print("  Skipped keys:", ", ".join(skipped))

    return 0


def cmd_mask(args: argparse.Namespace) -> int:
    """Print a masked version of a .env file to stdout."""
    env = load_env_file(args.file)
    masked = mask_env(env)
    print(serialize_env(masked))
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Manage snapshots of a .env file."""
    if args.snapshot_cmd == "create":
        path = create_snapshot(args.file, label=args.label)
        print(f"Snapshot created: {path}")

    elif args.snapshot_cmd == "list":
        entries = list_snapshots(args.file)
        if not entries:
            print("No snapshots found.")
        for entry in entries:
            label = f"  [{entry['label']}]" if entry.get("label") else ""
            print(f"{entry['id']}  {entry['timestamp']}{label}")

    elif args.snapshot_cmd == "restore":
        restore_snapshot(args.file, args.snapshot_id)
        print(f"Restored snapshot {args.snapshot_id} -> {args.file}")

    elif args.snapshot_cmd == "delete":
        delete_snapshot(args.file, args.snapshot_id)
        print(f"Deleted snapshot {args.snapshot_id}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="envoy",
        description="Manage and sync .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- diff ---
    p_diff = sub.add_parser("diff", help="Diff two .env files")
    p_diff.add_argument("source", help="Source .env file")
    p_diff.add_argument("target", help="Target .env file")
    p_diff.add_argument("--show-secrets", action="store_true", help="Reveal secret values in diff")
    p_diff.set_defaults(func=cmd_diff)

    # --- sync ---
    p_sync = sub.add_parser("sync", help="Sync keys from source into target")
    p_sync.add_argument("source", help="Source .env file")
    p_sync.add_argument("target", help="Target .env file")
    p_sync.add_argument("--overwrite", action="store_true", help="Overwrite existing keys")
    p_sync.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p_sync.set_defaults(func=cmd_sync)

    # --- mask ---
    p_mask = sub.add_parser("mask", help="Print masked .env file")
    p_mask.add_argument("file", help=".env file to mask")
    p_mask.set_defaults(func=cmd_mask)

    # --- snapshot ---
    p_snap = sub.add_parser("snapshot", help="Manage .env snapshots")
    p_snap.add_argument("file", help=".env file to snapshot")
    snap_sub = p_snap.add_subparsers(dest="snapshot_cmd", required=True)

    sc_create = snap_sub.add_parser("create", help="Create a snapshot")
    sc_create.add_argument("--label", default=None, help="Optional snapshot label")

    snap_sub.add_parser("list", help="List snapshots")

    sc_restore = snap_sub.add_parser("restore", help="Restore a snapshot")
    sc_restore.add_argument("snapshot_id", help="Snapshot ID to restore")

    sc_delete = snap_sub.add_parser("delete", help="Delete a snapshot")
    sc_delete.add_argument("snapshot_id", help="Snapshot ID to delete")

    p_snap.set_defaults(func=cmd_snapshot)

    # --- vault subcommands ---
    p_keygen = sub.add_parser("keygen", help="Generate an encryption key")
    p_keygen.add_argument("--output", default="envoy.key", help="Key file path")
    p_keygen.add_argument("--force", action="store_true", help="Overwrite existing key")
    p_keygen.set_defaults(func=cmd_keygen)

    p_encrypt = sub.add_parser("encrypt", help="Encrypt secret values in a .env file")
    p_encrypt.add_argument("file", help=".env file to encrypt")
    p_encrypt.add_argument("--key", default="envoy.key", help="Key file path")
    p_encrypt.add_argument("--output", default=None, help="Output file (default: overwrite)")
    p_encrypt.set_defaults(func=cmd_encrypt)

    p_decrypt = sub.add_="Decrypt secret values in a .env file")
    p_decrypt.add_argument("file", help=".env file to decrypt")
    p_decrypt.add_argument("--key", default="envoy.key", help="Key file path")
    p_decrypt.add_argument("--output", default=None, help="Output file (default: overwrite)")
    p_decrypt.set_defaults(func=cmd_decrypt)

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
