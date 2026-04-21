"""Redaction module: scrub secret values from env dicts before logging or display."""

from typing import Dict, List, Optional
from envoy.masking import is_secret, mask_value

REDACTED_PLACEHOLDER = "[REDACTED]"


def redact_env(
    env: Dict[str, str],
    extra_keys: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with secret values replaced by *placeholder*.

    Args:
        env: Mapping of env var names to values.
        extra_keys: Additional key names that should always be redacted,
                    regardless of the secret-detection heuristic.
        placeholder: String to substitute for secret values.

    Returns:
        New dict with the same keys but secret values replaced.
    """
    extra = set(k.upper() for k in (extra_keys or []))
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key.upper() in extra or is_secret(key):
            result[key] = placeholder
        else:
            result[key] = value
    return result


def redact_value(
    key: str,
    value: str,
    extra_keys: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> str:
    """Return *value* redacted if *key* is considered a secret."""
    extra = set(k.upper() for k in (extra_keys or []))
    if key.upper() in extra or is_secret(key):
        return placeholder
    return value


def diff_redacted(
    before: Dict[str, str],
    after: Dict[str, str],
    extra_keys: Optional[List[str]] = None,
) -> Dict[str, Dict[str, str]]:
    """Compare two env dicts and return changed keys with redacted values.

    Returns a mapping of key -> {"before": ..., "after": ...} for every key
    whose value changed between *before* and *after*.  Secret values are
    replaced with REDACTED_PLACEHOLDER so the result is safe to log.
    """
    all_keys = set(before) | set(after)
    changes: Dict[str, Dict[str, str]] = {}
    for key in sorted(all_keys):
        v_before = before.get(key)
        v_after = after.get(key)
        if v_before != v_after:
            changes[key] = {
                "before": redact_value(key, v_before, extra_keys)
                if v_before is not None
                else None,
                "after": redact_value(key, v_after, extra_keys)
                if v_after is not None
                else None,
            }
    return changes
