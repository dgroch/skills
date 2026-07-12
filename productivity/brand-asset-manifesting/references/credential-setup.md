# GWS Credential Setup for Background Jobs

## Credential Extraction

The credentials tarball at `/opt/data/workspace/gws_creds.tar` is NOT gzip-compressed. The correct extraction command is:

```bash
tar xf /opt/data/workspace/gws_creds.tar -C /tmp/gws_config/
```

**DO NOT use `tar xzf`** — it will fail with "not in gzip format".

## Required Environment Variables

When running gws in background processes or Python subprocesses, you must explicitly pass:

```python
env = {
    **os.environ,
    "GOOGLE_WORKSPACE_CLI_CONFIG_DIR": "/tmp/gws_config",
    "KEYRING_BACKEND": "file"
}
```

Both variables are required:
- `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`: Points to extracted credentials
- `KEYRING_BACKEND`: Must be "file" for non-interactive environments

## Shared Drive Listing Requirements

When listing files from a shared drive, the params JSON MUST include `"corpora": "drive"`:

```json
{
  "corpora": "drive",
  "driveId": "<SHARED_DRIVE_ID>",
  "includeItemsFromAllDrives": true,
  "supportsAllDrives": true,
  "pageSize": 1000
}
```

Without `corpora: "drive"`, you'll get: "The driveId parameter must be specified if and only if corpora is set to drive."

## Working Directory for Downloads

The gws `--output` flag only accepts CWD-relative paths. For downloads, run gws with `cwd="/tmp"`:

```python
subprocess.run(
    [GWS, "drive", "files", "get", "--params", params_json, "--output", "filename.jpg"],
    cwd="/tmp",
    env=env,
    ...
)
```

Then reference the downloaded file as `/tmp/filename.jpg`.

## Verification

After extracting credentials, verify they're accessible:

```bash
ls -la /tmp/gws_config/
# Should show credentials.json and token_cache.json
```

Test with a simple listing:

```bash
export GOOGLE_WORKSPACE_CLI_CONFIG_DIR=/tmp/gws_config
export KEYRING_BACKEND=file
gws drive files list --params '{"pageSize":1,"includeItemsFromAllDrives":true,"supportsAllDrives":true}' --format json
```
