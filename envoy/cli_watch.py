"""CLI commands for the watch feature."""

import argparse
import sys

from envoy.watch import watch_env_file
from envoy.display import display_diff
from envoy.masking import get_secret_keys
from envoy.parser import load_env_file


def _make_on_change(path: str, masked: bool) -> callable:
    """Return a callback that prints diffs to stdout."""

    def on_change(diff) -> None:
        try:
            env = load_env_file(path)
        except Exception:
            env = {}
        secret_keys = get_secret_keys(env) if masked else set()
        print(f"\n[envoy] Change detected in {path}")
        display_diff(diff, masked_keys=secret_keys)
        sys.stdout.flush()

    return on_change


def cmd_watch(args: argparse.Namespace) -> None:
    """
    Watch an .env file and print diffs when it changes.

    Exits cleanly on KeyboardInterrupt.
    """
    path: str = args.file
    interval: float = args.interval
    masked: bool = not args.no_mask

    print(f"[envoy] Watching {path} (interval={interval}s) — Ctrl+C to stop")
    sys.stdout.flush()

    try:
        watch_env_file(
            path=path,
            on_change=_make_on_change(path, masked),
            interval=interval,
        )
    except KeyboardInterrupt:
        print("\n[envoy] Watch stopped.")


def build_watch_subparser(subparsers) -> None:
    """Register the 'watch' subcommand on *subparsers*."""
    p = subparsers.add_parser(
        "watch",
        help="Watch an .env file for changes and display diffs.",
    )
    p.add_argument("file", help="Path to the .env file to watch.")
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0).",
    )
    p.add_argument(
        "--no-mask",
        action="store_true",
        default=False,
        help="Show secret values in plain text.",
    )
    p.set_defaults(func=cmd_watch)
