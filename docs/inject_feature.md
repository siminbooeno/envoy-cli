# Inject Feature

The `inject` command loads variables from a `.env` file and injects them into a
subprocess environment before running a given command. This is useful for running
tools that rely on environment variables without permanently exporting them to
your shell.

## Usage

```bash
# Run a command with all variables from .env injected
envoy inject .env -- python manage.py runserver

# Inject only specific keys
envoy inject .env --keys DATABASE_URL SECRET_KEY -- ./start.sh

# Preview what would be injected (dry-run, no command given)
envoy inject .env

# Do not overwrite variables already set in the shell
envoy inject .env --no-overwrite -- make test

# Verbose output showing injection counts
envoy inject .env -v -- pytest
```

## Options

| Option | Description |
|---|---|
| `env_file` | Path to the `.env` file to load. |
| `command` | Command and arguments to execute. Omit for a dry-run preview. |
| `--keys KEY [KEY ...]` | Restrict injection to the listed keys only. |
| `--overwrite` | Overwrite existing shell variables (default). |
| `--no-overwrite` | Preserve variables already set in the environment. |
| `-v, --verbose` | Print injection summary after the command exits. |

## Behaviour

- When no `command` is supplied, `inject` operates in **dry-run** mode and
  prints the keys that *would* be injected without executing anything.
- The exit code of `envoy inject` mirrors the exit code of the child process.
- Keys not present in the `.env` file are silently ignored when `--keys` is
  used with a key that does not exist.
