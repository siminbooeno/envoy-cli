"""Copy specific keys from one .env file to another."""

from dataclasses import dataclass, field
from typing import Optional
from envoy.parser import load_env_file, serialize_env


@dataclass
class CopyResult:
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def total_copied(self) -> int:
        return len(self.copied)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)

    @property
    def total_missing(self) -> int:
        return len(self.missing)

    def __repr__(self) -> str:
        return (
            f"CopyResult(copied={self.total_copied}, "
            f"skipped={self.total_skipped}, missing={self.total_missing})"
        )


def copy_keys(
    source: dict[str, str],
    target: dict[str, str],
    keys: list[str],
    overwrite: bool = False,
) -> tuple[dict[str, str], CopyResult]:
    """Copy selected keys from source into target dict."""
    result = CopyResult()
    output = dict(target)

    for key in keys:
        if key not in source:
            result.missing.append(key)
            continue
        if key in output and not overwrite:
            result.skipped.append(key)
            continue
        output[key] = source[key]
        result.copied.append(key)

    return output, result


def copy_env_file(
    source_path: str,
    target_path: str,
    keys: list[str],
    overwrite: bool = False,
    dest_path: Optional[str] = None,
) -> CopyResult:
    """Copy keys from source .env file into target .env file."""
    source = load_env_file(source_path)
    target = load_env_file(target_path) if dest_path or target_path else {}

    output, result = copy_keys(source, target, keys, overwrite=overwrite)

    out_path = dest_path or target_path
    with open(out_path, "w") as f:
        f.write(serialize_env(output))

    return result
