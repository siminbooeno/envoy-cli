"""Schema validation for .env files against a defined schema."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    URL = "url"
    EMAIL = "email"


@dataclass
class FieldSchema:
    type: FieldType = FieldType.STRING
    required: bool = False
    pattern: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SchemaViolation:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


@dataclass
class SchemaResult:
    violations: List[SchemaViolation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0

    def __str__(self) -> str:
        if self.is_valid:
            return "Schema validation passed."
        lines = ["Schema validation failed:"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


_BOOLEAN_VALUES = {"true", "false", "1", "0", "yes", "no"}
_URL_RE = re.compile(r"^https?://.+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_type(key: str, value: str, ftype: FieldType) -> Optional[SchemaViolation]:
    if ftype == FieldType.INTEGER:
        try:
            int(value)
        except ValueError:
            return SchemaViolation(key, f"expected integer, got {value!r}")
    elif ftype == FieldType.BOOLEAN:
        if value.lower() not in _BOOLEAN_VALUES:
            return SchemaViolation(key, f"expected boolean, got {value!r}")
    elif ftype == FieldType.URL:
        if not _URL_RE.match(value):
            return SchemaViolation(key, f"expected URL, got {value!r}")
    elif ftype == FieldType.EMAIL:
        if not _EMAIL_RE.match(value):
            return SchemaViolation(key, f"expected email, got {value!r}")
    return None


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, FieldSchema],
) -> SchemaResult:
    """Validate an env dict against a schema definition."""
    result = SchemaResult()

    for key, field_schema in schema.items():
        if key not in env:
            if field_schema.required:
                result.violations.append(
                    SchemaViolation(key, "required key is missing")
                )
            continue

        value = env[key]

        type_violation = _validate_type(key, value, field_schema.type)
        if type_violation:
            result.violations.append(type_violation)

        if field_schema.pattern and not re.fullmatch(field_schema.pattern, value):
            result.violations.append(
                SchemaViolation(
                    key,
                    f"value {value!r} does not match pattern {field_schema.pattern!r}",
                )
            )

    return result


def find_unknown_keys(
    env: Dict[str, str],
    schema: Dict[str, FieldSchema],
) -> List[str]:
    """Return a list of keys present in env that are not defined in the schema.

    Useful for detecting undocumented or unexpected environment variables.
    """
    return [key for key in env if key not in schema]
