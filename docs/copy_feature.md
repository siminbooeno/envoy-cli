# Copy Feature

The `copy` command lets you copy specific keys from one `.env` file into another.

## Usage

```bash
envoy copy <source> <target> KEY1 KEY2 [--overwrite] [--output FILE] [--dry-run]
```

## Arguments

| Argument | Description |
|---|---|
| `source` | Path to the source `.env` file |
| `target` | Path to the target `.env` file |
| `KEY1 KEY2 ...` | One or more keys to copy |

## Options

| Option | Description |
|---|---|
| `--overwrite` | Overwrite keys that already exist in the target |
| `--output FILE` | Write result to a new file instead of modifying target |
| `--dry-run` | Preview what would be copied without making changes |

## Examples

### Copy a single key

```bash
envoy copy .env.production .env.staging DB_HOST
```

### Copy multiple keys with overwrite

```bash
envoy copy .env.production .env.staging DB_HOST DB_PORT --overwrite
```

### Preview before copying

```bash
envoy copy .env.production .env.staging SECRET_KEY --dry-run
```

Output:
```
[dry-run] Would copy: SECRET_KEY=***
```

### Write to a separate output file

```bash
envoy copy .env.base .env.local APP_NAME PORT --output .env.merged
```

## Behaviour

- Keys **missing** from the source are reported but do not cause an error.
- Keys already present in the target are **skipped** unless `--overwrite` is set.
- The target file is updated in place unless `--output` is provided.
- A summary line is printed: `Done: N copied, N skipped, N missing.`
