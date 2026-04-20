"""CLI commands for viewing and managing the envoy audit log."""

import argparse
from envoy.audit import read_log, clear_log


def cmd_audit_log(args: argparse.Namespace) -> None:
    """Display audit log entries, optionally filtered by action."""
    entries = read_log(directory=args.dir)
    if not entries:
        print("No audit log entries found.")
        return

    filtered = entries
    if args.action:
        filtered = [e for e in entries if e["action"] == args.action]

    if not filtered:
        print(f"No entries found for action '{args.action}'.")
        return

    limit = args.limit if args.limit else len(filtered)
    shown = filtered[-limit:]

    for entry in shown:
        details_str = ""
        if entry.get("details"):
            parts = [f"{k}={v}" for k, v in entry["details"].items()]
            details_str = "  " + ", ".join(parts)
        print(f"[{entry['timestamp']}] {entry['action']:12s}  {entry['target']}{details_str}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    """Clear the audit log."""
    count = clear_log(directory=args.dir)
    if count == 0:
        print("Audit log was already empty.")
    else:
        print(f"Cleared {count} audit log entr{'y' if count == 1 else 'ies'}.")


def build_audit_subparser(subparsers) -> None:
    audit_parser = subparsers.add_parser("audit", help="View or manage the audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    log_p = audit_sub.add_parser("log", help="Show audit log entries")
    log_p.add_argument("--action", help="Filter by action type (e.g. sync, diff, encrypt)")
    log_p.add_argument("--limit", type=int, help="Show only the last N entries")
    log_p.add_argument("--dir", default=None, help="Directory containing the audit log")
    log_p.set_defaults(func=cmd_audit_log)

    clear_p = audit_sub.add_parser("clear", help="Clear the audit log")
    clear_p.add_argument("--dir", default=None, help="Directory containing the audit log")
    clear_p.set_defaults(func=cmd_audit_clear)
