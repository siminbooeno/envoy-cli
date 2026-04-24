"""Format .env file contents: sort keys, normalize quotes, align values."""

from typing import Dict, List, Optional, Tuple
from envoy.parser import parse_env_file, serialize_env


def sort_keys(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items()))


def group_by_prefix(env: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Group keys by their prefix (e.g. DB_HOST -> group 'DB')."""
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        prefix = key.split("_")[0] if "_" in key else key
        groups.setdefault(prefix, {})[key] = value
    return groups


def format_env(
    env: Dict[str, str],
    sort: bool = True,
    group: bool = False,
    comment_groups: bool = False,
) -> str:
    """Format an env dict into a canonical string representation.

    Args:
        env: The environment dictionary to format.
        sort: Whether to sort keys alphabetically.
        group: Whether to group keys by prefix with blank lines between groups.
        comment_groups: If grouping, add a comment header for each group.

    Returns:
        Formatted .env file content as a string.
    """
    if sort:
        env = sort_keys(env)

    if not group:
        return serialize_env(env)

    groups = group_by_prefix(env)
    sections: List[str] = []
    for prefix, members in groups.items():
        lines: List[str] = []
        if comment_groups:
            lines.append(f"# {prefix}")
        lines.append(serialize_env(members).rstrip())
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def format_env_file(
    path: str,
    sort: bool = True,
    group: bool = False,
    comment_groups: bool = False,
    dry_run: bool = False,
) -> Tuple[str, bool]:
    """Read, format, and optionally write an .env file.

    Returns:
        (formatted_content, changed) where changed is True if the content differs.
    """
    original = open(path, "r", encoding="utf-8").read()
    env = parse_env_file(path)
    formatted = format_env(env, sort=sort, group=group, comment_groups=comment_groups)
    changed = formatted != original
    if changed and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted)
    return formatted, changed
