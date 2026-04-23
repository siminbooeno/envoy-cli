# Tag Feature

The **tag** feature lets you annotate individual keys in a `.env` file with
arbitrary string tags (e.g. `secret`, `required`, `optional`, `deprecated`).
Tags are stored in a sidecar JSON file inside the `.envoy/` directory next to
your `.env` file and are never written into the env file itself.

## Storage

Tags are persisted at:
```
<env-file-dir>/.envoy/<env-filename>.tags.json
```

Example `production.env.tags.json`:
```json
{
  "API_KEY": ["secret", "required"],
  "DEBUG": ["optional"]
}
```

## Python API

```python
from pathlib import Path
from envoy.tag import add_tag, remove_tag, get_tags, keys_with_tag, all_tags

env = Path(".env")

# Add tags
add_tag(env, "API_KEY", "secret")
add_tag(env, "API_KEY", "required")

# Query
get_tags(env, "API_KEY")          # ["secret", "required"]
keys_with_tag(env, "secret")      # ["API_KEY", ...]
all_tags(env)                     # {"secret", "required", ...}

# Remove
remove_tag(env, "API_KEY", "required")
```

## CLI Usage

```bash
# Add a tag
envoy tag .env add API_KEY secret

# Remove a tag
envoy tag .env remove API_KEY secret

# List all tags in the file
envoy tag .env list

# List tags for a specific key
envoy tag .env list --key API_KEY

# Filter keys by tag
envoy tag .env filter secret
```
