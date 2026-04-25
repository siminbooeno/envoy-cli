"""Inject env values into a process environment or a command string."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.parser import load_env_file
from envoy.masking import mask_env


@dataclass
class InjectResult:
    injected: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    returncode: Optional[int] = None

    @property
    def total_injected(self) -> int:
        return len(self.injected)

    def __repr__(self) -> str:
        return (
            f"InjectResult(injected={self.total_injected}, "
            f"skipped={len(self.skipped)}, returncode={self.returncode})"
        )


def inject_env(
    env: Dict[str, str],
    base: Optional[Dict[str, str]] = None,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> InjectResult:
    """Build an environment dict by injecting *env* into *base*.

    Args:
        env: Key/value pairs to inject.
        base: Starting environment (defaults to current ``os.environ``).
        overwrite: When False, existing keys in *base* are preserved.
        keys: If given, only inject these specific keys.

    Returns:
        InjectResult with the merged environment and metadata.
    """
    base = dict(base if base is not None else os.environ)
    result = InjectResult()

    source = {k: v for k, v in env.items() if keys is None or k in keys}

    for key, value in source.items():
        if key in base and not overwrite:
            result.skipped.append(key)
        else:
            base[key] = value
            result.injected[key] = value

    return result


def inject_and_run(
    env_file: str,
    command: List[str],
    overwrite: bool = True,
    keys: Optional[List[str]] = None,
) -> InjectResult:
    """Load *env_file* and run *command* with the injected environment."""
    env = load_env_file(env_file)
    merged_base = dict(os.environ)
    result = inject_env(env, base=merged_base, overwrite=overwrite, keys=keys)

    run_env = {**merged_base, **result.injected}
    proc = subprocess.run(command, env=run_env)
    result.returncode = proc.returncode
    return result
