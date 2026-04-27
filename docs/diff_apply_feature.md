# diff-apply Feature

The `diff-apply` command lets you compute the diff between two env files and apply that diff onto a third (base) file. This is useful for propagating incremental changes across environments.

## Usage

```bash
envoy diff-apply <base> <source> <reference> [options]
```

### Arguments

| Argument    | Description                                      |
|-------------|--------------------------------------------------|
| `base`      | The `.env` file to patch                         |
| `source`    | The env file the diff is computed **from**       |
| `reference` | The env file the diff is computed **to**         |

### Options

| Flag              | Description                                        |
|-------------------|-------------------------------------------------|
| `-o / --output`   | Write result to a new file instead of overwriting `base` |
| `--overwrite`     | Apply changes even when keys already exist in base |
| `--keep-removed`  | Do not delete keys that were removed in the diff |
| `--dry-run`       | Preview without writing any files               |
| `-v / --verbose`  | Show per-key change details                     |

## Example

Suppose you have:

```
# staging.env (source)
DB_HOST=localhost
DB_PORT=5432

# production.env (reference)
DB_HOST=prod-db.internal
DB_PORT=5432
NEW_FEATURE=true
```

And you want to apply those changes onto `local.env`:

```bash
envoy diff-apply local.env staging.env production.env --overwrite -v
```

This will:
1. Compute the diff between `staging.env` → `production.env`
2. Apply that diff onto `local.env`
3. Add `NEW_FEATURE=true`
4. Update `DB_HOST` (if `--overwrite` is set)

## Conflict Handling

When a key exists in both `base` and the diff with different values, it is reported as a **conflict**. Without `--overwrite`, conflicts are skipped and listed in the output.

## Notes

- The `base` file is modified in-place unless `--output` is specified.
- Keys unchanged between `source` and `reference` are not touched in `base`.
