"""Promote .env values from one environment profile to another."""

from typing import Optional
from envoy.parser import load_env_file, serialize_env
from envoy.profile import get_profile, set_profile
from envoy.audit import log_event


def promote_keys(
    source: dict,
    target: dict,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> tuple[dict, list]:
    """Promote selected keys from source into target env dict.

    Returns updated target dict and list of promoted key names.
    """
    promoted = []
    result = dict(target)

    candidates = keys if keys is not None else list(source.keys())

    for key in candidates:
        if key not in source:
            continue
        if key in result and not overwrite:
            continue
        result[key] = source[key]
        promoted.append(key)

    return result, promoted


def promote_env_file(
    source_path: str,
    target_path: str,
    keys: Optional[list] = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> list:
    """Promote keys from source .env file into target .env file.

    Returns list of promoted key names.
    """
    source = load_env_file(source_path)
    target = load_env_file(target_path)

    updated, promoted = promote_keys(source, target, keys=keys, overwrite=overwrite)

    if not dry_run and promoted:
        content = serialize_env(updated)
        with open(target_path, "w") as f:
            f.write(content)

        log_event(
            action="promote",
            path=target_path,
            detail={
                "source": source_path,
                "promoted_keys": promoted,
                "overwrite": overwrite,
            },
        )

    return promoted
