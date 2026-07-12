---
name: background-credential-setup
description: Pattern for setting up gws credentials when running in background Python processes
---

# Background Credential Setup for gws

When running `gws` commands in background Python scripts (via `terminal(background=True)` or subprocess), the standard shell environment setup doesn't work. This causes credential discovery to fail even when credentials exist at `/tmp/gws_config/`.

## The Problem

Background processes don't inherit environment variables set with `set -a; source .env`. Additionally, gws credential discovery can fail silently even when `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` is set.

## The Solution

Explicitly pass an environment dictionary to `subprocess.run()` that includes both credential configuration variables:

```python
import subprocess
import os

# Build environment with explicit credential config
gws_env = {
    **os.environ,
    "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config",
    "KEYRING_BACKEND": "file"
}

# Use full path to gws (not in PATH for background processes)
gws_path = "/opt/data/npm-global/bin/gws"

# Example: list files
result = subprocess.run(
    [
        gws_path,
        "drive", "files", "list",
        "--params", '{"driveId":"0AOMVrKhhWKIwUk9PVA","includeItemsFromAllDrives":true,"supportsAllDrives":true,"pageSize":100}',
        "--format", "json"
    ],
    capture_output=True,
    text=True,
    env=gws_env,
    timeout=60
)

if result.returncode == 0:
    data = json.loads(result.stdout)
    files = data.get("files", [])
    print(f"Found {len(files)} files")
else:
    print(f"Error: {result.stderr}")
```

## Key Points

1. **Always use full path**: `/opt/data/npm-global/bin/gws` not just `gws`
2. **Explicit env dict**: Don't rely on inherited environment
3. **Both variables required**: `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` and `KEYRING_BACKEND`
4. **JSON params**: Use `--params` with JSON string, not individual flags
5. **Output format**: Use `--format json` for programmatic parsing

## Common Mistakes

❌ **Wrong**: Relying on shell environment
```bash
terminal(background=True, command="set -a; source .env; set +a; gws drive files list")
```

❌ **Wrong**: Setting only one env var
```python
env = {**os.environ, "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config"}
# Missing KEYRING_BACKEND
```

❌ **Wrong**: Using short command name
```python
subprocess.run(["gws", "drive", "list"], env=gws_env)
# gws not in PATH for background processes
```

✅ **Right**: Explicit full setup
```python
gws_env = {
    **os.environ,
    "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config",
    "KEYRING_BACKEND": "file"
}
subprocess.run(["/opt/data/npm-global/bin/gws", ...], env=gws_env)
```
