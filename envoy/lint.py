"""Lint .env files for common issues and best practices."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from envoy.parser import parse_env_file
from envoy.masking import is_secret


class Severity(str, Enum):
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


@dataclass
class LintIssue:
    line: int
    key: str
    message: str
    severity: Severity

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] line {self.line}: {self.key} — {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == Severity.ERROR)
        warnings = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        return f"{errors} error(s), {warnings} warning(s)"


def lint_env_file(path: str) -> LintResult:
    """Run all lint checks on a .env file and return a LintResult."""
    result = LintResult()
    env: Dict[str, str] = {}

    with open(path, "r") as f:
        raw_lines = f.readlines()

    for lineno, raw in enumerate(raw_lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            result.issues.append(LintIssue(
                line=lineno, key="?",
                message="Line is not a valid KEY=VALUE pair",
                severity=Severity.ERROR,
            ))
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key.replace("_", "").isalnum() or key[0].isdigit():
            result.issues.append(LintIssue(
                line=lineno, key=key,
                message="Key contains invalid characters or starts with a digit",
                severity=Severity.ERROR,
            ))

        if key != key.upper():
            result.issues.append(LintIssue(
                line=lineno, key=key,
                message="Key is not uppercase",
                severity=Severity.WARNING,
            ))

        if key in env:
            result.issues.append(LintIssue(
                line=lineno, key=key,
                message="Duplicate key detected",
                severity=Severity.ERROR,
            ))

        if is_secret(key) and value.strip() == "":
            result.issues.append(LintIssue(
                line=lineno, key=key,
                message="Secret key has an empty value",
                severity=Severity.WARNING,
            ))

        env[key] = value

    return result
