#!/usr/bin/env python3
"""
brand-cdn upload helper.

Uploads a local file or a remote URL to the brand-cdn Cloudflare Worker
and prints the public URL on stdout.

Usage:
    upload.py <bucket> <key> <source>
    upload.py --health

Where:
    <bucket>  R2 bucket name (e.g. whoosh, bower, figandbloom)
    <key>     Object key inside the bucket (e.g. characters/maya.png).
              Slashes are allowed and become path segments.
    <source>  Either a local file path or an http(s):// URL.

Reads WORKER_URL and an upload token from the first .env found in:
    1. /home/claude/.env       (Claude Code Execution)
    2. /opt/data/.env          (Hermes profile)
    3. ~/.env                  (fallback)

Either UPLOAD_TOKEN or BRAND_CDN_UPLOAD_TOKEN works as the var name. If
both are set, UPLOAD_TOKEN wins. The namespaced form is preferred when
the .env holds secrets for multiple skills.

Exit codes:
    0   Success. Public URL printed on stdout.
    1   Bad arguments or environment.
    2   Upload failed (network, auth, server error). Detail on stderr.
    3   Source could not be read or fetched.
"""

import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import mimetypes
from pathlib import Path


def load_env():
    """Load WORKER_URL and an upload token from a known .env location."""
    candidates = [
        Path("/home/claude/.env"),   # Claude Code Execution
        Path("/opt/data/.env"),       # Hermes profile
        Path.home() / ".env",         # standard fallback
    ]
    env_path = next((p for p in candidates if p.exists()), None)
    if env_path is None:
        sys.exit(
            "error: no .env found at /home/claude/.env, /opt/data/.env, "
            "or ~/.env. Add WORKER_URL and BRAND_CDN_UPLOAD_TOKEN."
        )

    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

    worker = env.get("WORKER_URL")
    # Accept BRAND_CDN_UPLOAD_TOKEN as an alias. UPLOAD_TOKEN wins if both set.
    token = env.get("UPLOAD_TOKEN") or env.get("BRAND_CDN_UPLOAD_TOKEN")
    if not worker or not token:
        sys.exit(
            f"error: WORKER_URL or UPLOAD_TOKEN/BRAND_CDN_UPLOAD_TOKEN "
            f"missing from {env_path}"
        )
    return worker.rstrip("/"), token


def health_check(worker_url):
    """Hit /health, expect 'ok'. Exits non-zero on failure."""
    try:
        req = urllib.request.Request(
            f"{worker_url}/health",
            headers={"User-Agent": "brand-cdn-upload/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode().strip()
            if body == "ok":
                print("ok")
                return
            sys.exit(f"error: unexpected health response: {body!r}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace").strip()
        sys.exit(f"error: HTTP {e.code} from worker: {msg}")
    except Exception as e:
        sys.exit(f"error: {e}")


def read_source(source):
    """Return (bytes, content_type) for a local path or http(s) URL."""
    if source.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "brand-cdn-upload/1.0"},
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                ct = r.headers.get("Content-Type", "application/octet-stream")
                return data, ct
        except Exception as e:
            print(f"error: could not fetch {source}: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        path = Path(source).expanduser()
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(3)
        try:
            data = path.read_bytes()
        except Exception as e:
            print(f"error: could not read {path}: {e}", file=sys.stderr)
            sys.exit(3)
        ct, _ = mimetypes.guess_type(str(path))
        if not ct:
            ct = "application/octet-stream"
        return data, ct


def upload(worker_url, token, bucket, key, source):
    data, content_type = read_source(source)

    # URL-encode each path segment of the key but keep the slashes
    safe_key = "/".join(
        urllib.parse.quote(seg, safe="") for seg in key.split("/")
    )
    target = f"{worker_url}/upload/{bucket}/{safe_key}"

    req = urllib.request.Request(
        target,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
            "User-Agent": "brand-cdn-upload/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read().decode()
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                print(f"error: non-JSON response: {body}", file=sys.stderr)
                sys.exit(2)
            if not payload.get("ok"):
                print(f"error: upload failed: {body}", file=sys.stderr)
                sys.exit(2)
            print(payload["url"])
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace").strip()
        deny = e.headers.get("x-deny-reason")
        if deny == "host_not_allowed":
            print(
                "error: worker host is not in the runtime's network allowlist. "
                "Add brand-cdn.figandbloom.workers.dev to the agent's allowed "
                "domains (Claude.ai: Settings → Capabilities → Code execution "
                "→ Allowed domains; Hermes: profile network config).",
                file=sys.stderr,
            )
            sys.exit(2)
        if e.code == 401:
            print(
                "error: 401 unauthorized — token in .env doesn't match the "
                "Worker's secret. Ask the user to confirm or rotate.",
                file=sys.stderr,
            )
            sys.exit(2)
        print(f"error: HTTP {e.code} from worker: {msg}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    if args[0] == "--health":
        worker_url, _ = load_env()
        health_check(worker_url)
        return

    if len(args) != 3:
        sys.exit(__doc__)

    bucket, key, source = args
    worker_url, token = load_env()
    upload(worker_url, token, bucket, key, source)


if __name__ == "__main__":
    main()
