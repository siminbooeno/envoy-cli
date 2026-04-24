"""Type casting utilities for .env values."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional


class CastError(ValueError):
    """Raised when a value cannot be cast to the requested type."""

    def __init__(self, key: str, value: str, target: str) -> None:
        self.key = key
        self.value = value
        self.target = target
        super().__init__(
            f"Cannot cast '{key}={value!r}' to {target}"
        )


_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


def cast_bool(key: str, value: str) -> bool:
    """Cast a string value to bool."""
    normalized = value.strip().lower()
    if normalized in _TRUTHY:
        return True
    if normalized in _FALSY:
        return False
    raise CastError(key, value, "bool")


def cast_int(key: str, value: str) -> int:
    """Cast a string value to int."""
    try:
        return int(value.strip())
    except ValueError:
        raise CastError(key, value, "int")


def cast_float(key: str, value: str) -> float:
    """Cast a string value to float."""
    try:
        return float(value.strip())
    except ValueError:
        raise CastError(key, value, "float")


def cast_list(key: str, value: str, delimiter: str = ",") -> List[str]:
    """Cast a delimited string value to a list of stripped strings."""
    return [item.strip() for item in value.split(delimiter) if item.strip()]


def cast_value(key: str, value: str, target: str, **kwargs: Any) -> Any:
    """Dispatch casting by target type name.

    Supported targets: 'str', 'int', 'float', 'bool', 'list'.
    """
    target = target.strip().lower()
    if target == "str":
        return value
    if target == "int":
        return cast_int(key, value)
    if target == "float":
        return cast_float(key, value)
    if target == "bool":
        return cast_bool(key, value)
    if target == "list":
        delimiter = kwargs.get("delimiter", ",")
        return cast_list(key, value, delimiter=delimiter)
    raise ValueError(f"Unknown target type: {target!r}")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
    *,
    strict: bool = False,
    delimiter: str = ",",
) -> Dict[str, Any]:
    """Apply type casting to an env dict using a schema mapping key -> type.

    Keys not in the schema are kept as plain strings.
    If *strict* is True, CastError propagates; otherwise the raw string is kept.
    """
    result: Dict[str, Any] = {}
    for key, value in env.items():
        target = schema.get(key)
        if target is None:
            result[key] = value
            continue
        try:
            result[key] = cast_value(key, value, target, delimiter=delimiter)
        except CastError:
            if strict:
                raise
            result[key] = value
    return result
