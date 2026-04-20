"""Export .env data to various formats: shell, JSON, Docker."""

import json
from typing import Dict, Optional

from envoy.masking import mask_env


EXPORT_FORMATS = ("shell", "json", "docker")


def export_shell(env: Dict[str, str], masked: bool = False) -> str:
    """Export env vars as shell export statements."""
    data = mask_env(env) if masked else env
    lines = [f'export {key}="{value}"' for key, value in sorted(data.items())]
    return "\n".join(lines)


def export_json(env: Dict[str, str], masked: bool = False) -> str:
    """Export env vars as a JSON object."""
    data = mask_env(env) if masked else env
    return json.dumps(dict(sorted(data.items())), indent=2)


def export_docker(env: Dict[str, str], masked: bool = False) -> str:
    """Export env vars as Docker --env-file compatible format (KEY=VALUE)."""
    data = mask_env(env) if masked else env
    lines = [f"{key}={value}" for key, value in sorted(data.items())]
    return "\n".join(lines)


def export_env(
    env: Dict[str, str],
    fmt: str = "shell",
    masked: bool = False,
    output_path: Optional[str] = None,
) -> str:
    """Export env to the given format. Optionally write to a file."""
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(EXPORT_FORMATS)}")

    exporters = {
        "shell": export_shell,
        "json": export_json,
        "docker": export_docker,
    }

    result = exporters[fmt](env, masked=masked)

    if output_path:
        with open(output_path, "w") as f:
            f.write(result + "\n")

    return result
