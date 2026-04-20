"""Template rendering for .env files using variable substitution."""

import re
from typing import Optional

_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def render_template(template: str, context: dict[str, str], strict: bool = False) -> str:
    """Render a template string by substituting ${VAR} or $VAR placeholders.

    Args:
        template: The template string containing variable references.
        context: A mapping of variable names to their values.
        strict: If True, raise KeyError for missing variables. Otherwise leave them as-is.

    Returns:
        The rendered string with substitutions applied.
    """
    def replace(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in context:
            return context[key]
        if strict:
            raise KeyError(f"Template variable '{key}' not found in context")
        return match.group(0)

    return _VAR_PATTERN.sub(replace, template)


def render_env_template(
    env_template: dict[str, str],
    context: dict[str, str],
    strict: bool = False,
) -> dict[str, str]:
    """Render all values in an env dict as templates.

    Args:
        env_template: Dict of env key -> value (possibly containing placeholders).
        context: Variable context for substitution.
        strict: If True, raise on missing variables.

    Returns:
        New dict with all values rendered.
    """
    return {
        key: render_template(value, context, strict=strict)
        for key, value in env_template.items()
    }


def collect_variables(template: str) -> list[str]:
    """Return a sorted list of unique variable names referenced in a template string."""
    matches = _VAR_PATTERN.findall(template)
    variables = {m[0] or m[1] for m in matches}
    return sorted(variables)


def missing_variables(env_template: dict[str, str], context: dict[str, str]) -> list[str]:
    """Return variable names referenced in any template value but absent from context."""
    all_vars: set[str] = set()
    for value in env_template.values():
        all_vars.update(collect_variables(value))
    return sorted(all_vars - context.keys())
