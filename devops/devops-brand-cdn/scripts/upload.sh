#!/usr/bin/env bash
#
# brand-cdn upload helper (bash entry point).
#
# Usage:
#   upload.sh <bucket> <key> <source>
#   upload.sh --health
#
# <source> can be a local file path or an http(s):// URL.
#
# Reads WORKER_URL and an upload token from the first .env found in:
#   1. /home/claude/.env      (Claude Code Execution)
#   2. /opt/data/.env         (Hermes profile)
#   3. $HOME/.env             (fallback)
#
# Either UPLOAD_TOKEN or BRAND_CDN_UPLOAD_TOKEN works. UPLOAD_TOKEN wins
# if both are set. Namespaced form preferred for multi-skill .envs.
#
# This script prefers curl when available. If curl is missing (e.g.
# minimal Hermes runtimes), it delegates to upload.py — which uses
# Python urllib with the User-Agent header that Cloudflare's WAF requires.
#
# Prints the public URL on stdout on success.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- runtime check: prefer curl, fall back to python3 via upload.py ---
if ! command -v curl >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1 && [[ -f "${SCRIPT_DIR}/upload.py" ]]; then
    exec python3 "${SCRIPT_DIR}/upload.py" "$@"
  fi
  echo "error: this script needs curl, or python3 with upload.py present. Neither found." >&2
  exit 1
fi

# --- env loading ---
ENV_FILE=""
for candidate in /home/claude/.env /opt/data/.env "${HOME}/.env"; do
  if [[ -f "$candidate" ]]; then
    ENV_FILE="$candidate"
    break
  fi
done

if [[ -z "$ENV_FILE" ]]; then
  echo "error: no .env found at /home/claude/.env, /opt/data/.env, or ~/.env. Add WORKER_URL and BRAND_CDN_UPLOAD_TOKEN (or UPLOAD_TOKEN)." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

# Accept BRAND_CDN_UPLOAD_TOKEN as an alias for UPLOAD_TOKEN.
UPLOAD_TOKEN="${UPLOAD_TOKEN:-${BRAND_CDN_UPLOAD_TOKEN:-}}"

if [[ -z "${WORKER_URL:-}" || -z "${UPLOAD_TOKEN:-}" ]]; then
  echo "error: WORKER_URL or UPLOAD_TOKEN/BRAND_CDN_UPLOAD_TOKEN missing from $ENV_FILE" >&2
  exit 1
fi

WORKER_URL="${WORKER_URL%/}"

# --- health check ---
if [[ "${1:-}" == "--health" ]]; then
  body=$(curl -sS -A "brand-cdn-upload/1.0" -w "\n%{http_code}" "${WORKER_URL}/health")
  code=$(echo "$body" | tail -n1)
  text=$(echo "$body" | sed '$d')
  if [[ "$code" == "200" && "$text" == "ok" ]]; then
    echo "ok"
    exit 0
  fi
  echo "error: health check failed (HTTP $code): $text" >&2
  exit 2
fi

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <bucket> <key> <source>" >&2
  echo "       $0 --health" >&2
  exit 1
fi

BUCKET="$1"
KEY="$2"
SOURCE="$3"

# Resolve the source to a local file. If it's a URL, download to a tempfile.
TMP=""
cleanup() { [[ -n "$TMP" && -f "$TMP" ]] && rm -f "$TMP"; }
trap cleanup EXIT

if [[ "$SOURCE" =~ ^https?:// ]]; then
  TMP=$(mktemp)
  if ! curl -sSL -A "brand-cdn-upload/1.0" -o "$TMP" "$SOURCE"; then
    echo "error: could not fetch $SOURCE" >&2
    exit 3
  fi
  LOCAL="$TMP"
else
  if [[ ! -f "$SOURCE" ]]; then
    echo "error: file not found: $SOURCE" >&2
    exit 3
  fi
  LOCAL="$SOURCE"
fi

# Detect content type
if command -v file >/dev/null 2>&1; then
  CT=$(file --mime-type -b "$LOCAL" 2>/dev/null || echo "application/octet-stream")
else
  CT="application/octet-stream"
fi

# URL-encode the key path segments (keep slashes)
ENCODED_KEY=$(python3 -c "
import sys, urllib.parse
k = sys.argv[1]
print('/'.join(urllib.parse.quote(s, safe='') for s in k.split('/')))
" "$KEY")

TARGET="${WORKER_URL}/upload/${BUCKET}/${ENCODED_KEY}"

response=$(curl -sS -w "\n%{http_code}" \
  -X POST \
  -A "brand-cdn-upload/1.0" \
  -H "Authorization: Bearer ${UPLOAD_TOKEN}" \
  -H "Content-Type: ${CT}" \
  --data-binary "@${LOCAL}" \
  -D /tmp/_brand-cdn-headers.$$ \
  "$TARGET")

code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [[ "$code" == "200" ]]; then
  # Worker returns JSON like {"ok":true,"url":"https://..."}
  url=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['url'])" 2>/dev/null || true)
  if [[ -n "$url" ]]; then
    echo "$url"
    rm -f /tmp/_brand-cdn-headers.$$
    exit 0
  fi
fi

# Failure path — give the caller something useful
deny=$(grep -i '^x-deny-reason:' /tmp/_brand-cdn-headers.$$ 2>/dev/null | tr -d '\r' | cut -d: -f2- | xargs || true)
rm -f /tmp/_brand-cdn-headers.$$

if [[ "$deny" == "host_not_allowed" ]]; then
  cat >&2 <<EOF
error: worker host is not in the runtime's network allowlist.
Add brand-cdn.figandbloom.workers.dev to the agent's allowed domains
(Claude.ai: Settings → Capabilities → Code execution → Allowed domains;
Hermes: profile network config), then retry.
EOF
  exit 2
fi

if [[ "$code" == "401" ]]; then
  echo "error: 401 unauthorized — token doesn't match the Worker's secret." >&2
  exit 2
fi

echo "error: HTTP $code from worker: $body" >&2
exit 2
