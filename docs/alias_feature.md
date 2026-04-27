# Alias Feature

The **alias** feature lets you define shorthand names for existing keys in an `.env` file. Aliases are stored in a sidecar JSON file (`.envoy/<stem>.aliases.json`) and never modify the original `.env`.

## Use Cases

- Expose a long key like `DATABASE_PRIMARY_HOST` under a shorter alias `DB_HOST`.
- Allow legacy key names to coexist with new canonical names during migrations.
- Generate expanded env dicts that include both the original and aliased keys.

## CLI Usage

```bash
# Add an alias
envoy alias .env add HOST DB_HOST

# Remove an alias
envoy alias .env remove HOST

# Resolve an alias to its original key
envoy alias .env resolve HOST

# List all aliases
envoy alias .env list
```

## Python API

```python
from pathlib import Path
from envoy.alias import add_alias, resolve_alias, apply_aliases, list_aliases

env_file = Path(".env")

# Register alias
add_alias(env_file, "HOST", "DB_HOST")

# Resolve
original = resolve_alias(env_file, "HOST")  # -> "DB_HOST"

# Apply to an env dict
env = {"DB_HOST": "localhost"}
expanded = apply_aliases(env, {"HOST": "DB_HOST"})
# expanded == {"DB_HOST": "localhost", "HOST": "localhost"}
```

## Storage Format

Aliases are stored as a flat JSON object:

```json
{
  "HOST": "DB_HOST",
  "PASS": "DB_PASSWORD"
}
```

The file lives at `.envoy/<env-stem>.aliases.json` relative to the `.env` file.

## Notes

- Aliases do **not** replace or rename keys in the original file.
- `apply_aliases` returns a **copy** — the original dict is never mutated.
- If the original key is absent from the env dict, the alias is silently skipped.
