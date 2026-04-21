"""Validate .env file values against simple rules (non-empty, regex, allowed values)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class RuleType(str, Enum):
    NON_EMPTY = "non_empty"
    REGEX = "regex"
    ALLOWED = "allowed"
    MIN_LENGTH = "min_length"


@dataclass
class ValidationError:
    key: str
    rule: RuleType
    message: str

    def __str__(self) -> str:
        return f"[{self.rule.value}] {self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def add(self, key: str, rule: RuleType, message: str) -> None:
        self.errors.append(ValidationError(key=key, rule=rule, message=message))

    def summary(self) -> str:
        if self.valid:
            return "All validations passed."
        lines = [f"{len(self.errors)} validation error(s):"] + [f"  {e}" for e in self.errors]
        return "\n".join(lines)


def validate_non_empty(env: Dict[str, str], keys: List[str], result: ValidationResult) -> None:
    for key in keys:
        if env.get(key, "").strip() == "":
            result.add(key, RuleType.NON_EMPTY, "value must not be empty")


def validate_regex(env: Dict[str, str], rules: Dict[str, str], result: ValidationResult) -> None:
    for key, pattern in rules.items():
        value = env.get(key)
        if value is None:
            continue
        if not re.fullmatch(pattern, value):
            result.add(key, RuleType.REGEX, f"value {value!r} does not match pattern {pattern!r}")


def validate_allowed(env: Dict[str, str], rules: Dict[str, List[str]], result: ValidationResult) -> None:
    for key, allowed in rules.items():
        value = env.get(key)
        if value is None:
            continue
        if value not in allowed:
            result.add(key, RuleType.ALLOWED, f"value {value!r} not in allowed set {allowed}")


def validate_min_length(env: Dict[str, str], rules: Dict[str, int], result: ValidationResult) -> None:
    for key, min_len in rules.items():
        value = env.get(key, "")
        if len(value) < min_len:
            result.add(key, RuleType.MIN_LENGTH, f"value length {len(value)} is less than minimum {min_len}")


def validate_env(
    env: Dict[str, str],
    non_empty: Optional[List[str]] = None,
    regex: Optional[Dict[str, str]] = None,
    allowed: Optional[Dict[str, List[str]]] = None,
    min_length: Optional[Dict[str, int]] = None,
) -> ValidationResult:
    result = ValidationResult()
    if non_empty:
        validate_non_empty(env, non_empty, result)
    if regex:
        validate_regex(env, regex, result)
    if allowed:
        validate_allowed(env, allowed, result)
    if min_length:
        validate_min_length(env, min_length, result)
    return result
