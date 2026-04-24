# Filter Feature

The `filter` command lets you narrow down the entries in a `.env` file using one or more criteria.

## Usage

```bash
envoy filter <file> [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--prefix PREFIX` | Keep only keys that start with the given prefix |
| `--pattern REGEX` | Keep only keys matching the given regular expression |
| `--value-pattern REGEX` | Keep only entries whose **value** matches the regex |
| `--exclude-empty` | Drop entries with blank/empty values |
| `--output FILE` | Write the filtered result to a file instead of stdout |
| `--masked` | Mask secret values (keys containing `SECRET`, `KEY`, `TOKEN`, etc.) |
| `--verbose` | Show counts of matched and excluded entries |

## Examples

### Filter by prefix

```bash
envoy filter .env --prefix APP_
```

Outputs only keys like `APP_NAME`, `APP_ENV`, etc.

### Filter by regex pattern

```bash
envoy filter .env --pattern '^DB_'
```

### Filter by value content

```bash
envoy filter .env --value-pattern 'localhost'
```

### Combine filters

Filters are applied in sequence — prefix first, then pattern, then value-pattern, then empty exclusion:

```bash
envoy filter .env --prefix DB_ --exclude-empty
```

### Write to file

```bash
envoy filter .env --prefix APP_ --output filtered.env
```

### Mask secrets in output

```bash
envoy filter .env --masked
```

## Python API

```python
from envoy.filter import filter_env

env = {"APP_NAME": "myapp", "DB_HOST": "localhost", "SECRET_KEY": "s3cr3t"}
result = filter_env(env, prefix="APP_")
print(result.matched)   # {"APP_NAME": "myapp"}
print(result.excluded)  # {"DB_HOST": ..., "SECRET_KEY": ...}
```
