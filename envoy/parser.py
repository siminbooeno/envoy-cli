"""Parser for .env files with support for comments, quoted values, and multiline."""

import re
from typing import Dict, Tuple

ENV_LINE_RE = re.compile(
    r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$'
)


def parse_env_file(content: str) -> Dict[str, str]:
    """Parse .env file content into a key-value dictionary."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = ENV_LINE_RE.match(line)
        if match:
            key = match.group('key')
            value = _strip_quotes(match.group('value').strip())
            result[key] = value
    return result


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
    return value


def serialize_env(data: Dict[str, str]) -> str:
    """Serialize a key-value dictionary back to .env file format."""
    lines = []
    for key, value in sorted(data.items()):
        if ' ' in value or '#' in value or not value:
            value = f'"{value}"'
        lines.append(f'{key}={value}')
    return '\n'.join(lines) + '\n'


def load_env_file(path: str) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    with open(path, 'r', encoding='utf-8') as f:
        return parse_env_file(f.read())
