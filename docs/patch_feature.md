# Patch Feature

The `patch` command lets you apply targeted key-value changes to an existing
`.env` file without rewriting it from scratch.

## Usage

```
envoy patch <file> [--set KEY=VALUE ...] [--remove KEY ...] [--no-overwrite] [--dry-run]
```

### Options

| Flag | Description |
|---|---|
| `--set KEY=VALUE` | Add or update a key. Repeatable. |
| `--remove KEY` | Delete a key. Repeatable. |
| `--no-overwrite` | Skip keys that already exist (only add new ones). |
| `--dry-run` | Preview changes without writing to disk. |

## Examples

### Set a single key
```bash
envoy patch .env --set APP_ENV=production
```

### Set multiple keys at once
```bash
envoy patch .env --set DB_HOST=db.prod --set DB_PORT=5432
```

### Remove a key
```bash
envoy patch .env --remove LEGACY_FLAG
```

### Combine set and remove
```bash
envoy patch .env --set NEW_KEY=value --remove OLD_KEY
```

### Preview without writing
```bash
envoy patch .env --set DEBUG=false --dry-run
```

### Add only (skip existing)
```bash
envoy patch .env --set APP_NAME=myapp --no-overwrite
```

## Output symbols

| Symbol | Meaning |
|---|---|
| `+` | Key was added |
| `~` | Key was updated |
| `-` | Key was removed |
| `=` | Key was skipped |

## Python API

```python
from envoy.patch import patch_env, patch_env_file

# Pure dict API
env = {"APP": "hello", "DEBUG": "true"}
patched, report = patch_env(env, {"APP": "world", "DEBUG": None})
print(report.updated)  # ['APP']
print(report.removed)  # ['DEBUG']

# File API
report = patch_env_file(".env", {"VERSION": "2.0"}, dry_run=True)
```
