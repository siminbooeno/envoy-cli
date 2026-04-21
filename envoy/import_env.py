"""Import env variables from external sources (OS environment, JSON, YAML)."""

import json
import os
from typing import Dict, Optional


def import_from_os(prefix: Optional[str] = None) -> Dict[str, str]:
    """Import variables from the current OS environment.

    Args:
        prefix: If given, only import variables starting with this prefix.
                The prefix is stripped from the resulting keys.

    Returns:
        A dict of key/value pairs.
    """
    result: Dict[str, str] = {}
    for key, value in os.environ.items():
        if prefix:
            if key.startswith(prefix):
                stripped = key[len(prefix):]
                if stripped:  # avoid empty keys after stripping
                    result[stripped] = value
        else:
            result[key] = value
    return result


def import_from_json(path: str) -> Dict[str, str]:
    """Import variables from a JSON file (flat key/value object).

    Args:
        path: Path to the JSON file.

    Returns:
        A dict of key/value pairs (values coerced to str).

    Raises:
        ValueError: If the JSON is not a flat object.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object at top level, got {type(data).__name__}")

    result: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            raise ValueError(f"Nested objects are not supported (key '{k}')")
        result[str(k)] = str(v) if not isinstance(v, bool) else str(v).lower()
    return result


def import_from_dotenv_string(content: str) -> Dict[str, str]:
    """Parse a raw .env-formatted string and return a dict.

    Useful for importing env content received from stdin or a remote source
    without writing to disk first.

    Args:
        content: Raw .env file content as a string.

    Returns:
        A dict of key/value pairs.
    """
    from envoy.parser import parse_env_file
    import tempfile, os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return parse_env_file(tmp_path)
    finally:
        os.unlink(tmp_path)


def merge_imported(base: Dict[str, str], imported: Dict[str, str], overwrite: bool = False) -> Dict[str, str]:
    """Merge imported variables into a base dict.

    Args:
        base:      Existing env variables.
        imported:  Newly imported variables.
        overwrite: If True, imported values overwrite existing ones.

    Returns:
        Merged dict.
    """
    result = dict(base)
    for key, value in imported.items():
        if key not in result or overwrite:
            result[key] = value
    return result
