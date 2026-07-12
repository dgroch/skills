# GWS Credential Extraction and Authentication

## Credential Location
GWS credentials are stored encrypted in `/opt/data/workspace/gws_creds.tar`.

## Extraction Workflow
```bash
mkdir -p /tmp/gws_config
tar xzf /opt/data/workspace/gws_creds.tar -C /tmp/gws_config/
```

## Environment Setup
```bash
export PATH=/opt/data/npm-global/bin:$PATH
export GOOGLE_WORKSPACE_CLI_CONFIG_DIR=/tmp/gws_config
export KEYRING_BACKEND=file
```

## Verify Authentication
```bash
gws auth status
```

Expected output:
- `auth_method`: `oauth2`
- `token_valid`: `true`
- `user`: `admin@figandbloom.com.au`
- `storage`: `encrypted`

## Common Issues

### "Access denied. No credentials provided"
- Ensure `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=/tmp/gws_config` is set
- Verify credentials were extracted: `ls /tmp/gws_config/` should show `.encryption_key`, `credentials.enc`, `token_cache.json`
- Check keyring backend: `KEYRING_BACKEND=file` (not default `keyring`)

### "Cannot read client_secret.json: stream did not contain valid UTF-8"
- This is expected for encrypted credentials
- GWS handles decryption internally using `.encryption_key`
- Ignore this warning in `auth status` output

### Token Expiration
- GWS auto-refreshes tokens using `credentials.enc`
- If operations fail with 401, re-run `gws auth status` to trigger refresh
- Token cache is in `/tmp/gws_config/cache/` (drive_v3.json, etc.)
