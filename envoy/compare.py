"""Compare two .env files and produce a structured report."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file
from envoy.diff import compute_diff, ChangeType, EnvDiff
from envoy.masking import is_secret, mask_value


@dataclass
class CompareReport:
    source_path: str
    target_path: str
    diffs: List[EnvDiff] = field(default_factory=list)
    source_only: List[str] = field(default_factory=list)
    target_only: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    common: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.source_only or self.target_only or self.changed)

    @property
    def summary(self) -> Dict[str, int]:
        return {
            "added": len(self.source_only),
            "removed": len(self.target_only),
            "changed": len(self.changed),
            "common": len(self.common),
        }


def compare_env_files(
    source_path: str,
    target_path: str,
    mask_secrets: bool = False,
) -> CompareReport:
    """Compare two env files and return a structured CompareReport."""
    source_env = load_env_file(source_path)
    target_env = load_env_file(target_path)

    if mask_secrets:
        source_env = {
            k: (mask_value(v) if is_secret(k) else v)
            for k, v in source_env.items()
        }
        target_env = {
            k: (mask_value(v) if is_secret(k) else v)
            for k, v in target_env.items()
        }

    diffs = compute_diff(source_env, target_env)

    source_only = [d.key for d in diffs if d.change == ChangeType.ADDED]
    target_only = [d.key for d in diffs if d.change == ChangeType.REMOVED]
    changed = [d.key for d in diffs if d.change == ChangeType.MODIFIED]
    all_diff_keys = set(source_only + target_only + changed)
    common = [
        k for k in source_env if k in target_env and k not in all_diff_keys
    ]

    return CompareReport(
        source_path=source_path,
        target_path=target_path,
        diffs=diffs,
        source_only=source_only,
        target_only=target_only,
        changed=changed,
        common=common,
    )


def format_report(report: CompareReport, verbose: bool = False) -> str:
    """Render a CompareReport as a human-readable string."""
    lines = [
        f"Comparing: {report.source_path} → {report.target_path}",
        f"  Added  : {len(report.source_only)}",
        f"  Removed: {len(report.target_only)}",
        f"  Changed: {len(report.changed)}",
        f"  Common : {len(report.common)}",
    ]
    if verbose and report.has_differences:
        lines.append("")
        for diff in report.diffs:
            tag = diff.change.value.upper().ljust(8)
            old = f"  old={diff.old_value!r}" if diff.old_value is not None else ""
            new = f"  new={diff.new_value!r}" if diff.new_value is not None else ""
            lines.append(f"  [{tag}] {diff.key}{old}{new}")
    return "\n".join(lines)
