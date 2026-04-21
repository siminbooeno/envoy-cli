"""Resolve environment variable references within a .env file.

Supports ${VAR} and $VAR style self-references so values can be built
from other keys defined in the same file.
"""

import re
from typing import Dict, Optional

_REF_PATTERN = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')


class ResolutionError(Exception):
    """Raised when a variable reference cannot be resolved."""


def resolve_value(value: str, env: Dict[str, str], strict: bool = False) -> str:
    """Replace variable references in *value* using keys from *env*.

    Args:
        value:  The raw value string, possibly containing $VAR or ${VAR}.
        env:    Mapping of known key→value pairs to draw from.
        strict: If True, raise ResolutionError for unknown references.
                If False, leave unresolvable placeholders as-is.

    Returns:
        The value with all resolvable references substituted.
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in env:
            return env[key]
        if strict:
            raise ResolutionError(f"Undefined variable reference: '{key}'")
        return match.group(0)  # leave placeholder intact

    return _REF_PATTERN.sub(_replace, value)


def resolve_env(
    env: Dict[str, str],
    strict: bool = False,
    max_passes: int = 5,
) -> Dict[str, str]:
    """Resolve all cross-references in *env* iteratively.

    Multiple passes are performed to handle chained references
    (e.g. C=${B}, B=${A}, A=hello).

    Args:
        env:        The environment dict to resolve.
        strict:     Propagated to :func:`resolve_value`.
        max_passes: Maximum number of resolution iterations.

    Returns:
        A new dict with all resolvable references expanded.
    """
    resolved = dict(env)
    for _ in range(max_passes):
        updated = {
            k: resolve_value(v, resolved, strict=strict)
            for k, v in resolved.items()
        }
        if updated == resolved:
            break
        resolved = updated
    return resolved


def unresolved_references(env: Dict[str, str]) -> Dict[str, list]:
    """Return a mapping of key → list of unresolved reference names.

    Useful for reporting which keys still contain dangling placeholders
    after resolution.
    """
    result: Dict[str, list] = {}
    for key, value in env.items():
        refs = [
            m.group(1) or m.group(2)
            for m in _REF_PATTERN.finditer(value)
            if (m.group(1) or m.group(2)) not in env
        ]
        if refs:
            result[key] = refs
    return result
