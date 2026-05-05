#!/bin/bash
# run_firecrawl.sh — lightweight cron entry point
#
# Usage:
#   ./run_firecrawl.sh              # all sources, full limit
#   ./run_firecrawl.sh --dry-run    # test without writing
#   ./run_firecrawl.sh --limit 50   # cap at 50 new reviews
#
# Env:
#   FIRECRAWL_API_KEY  — from ~/.env or parent environment
#   HERMES_AGENT_HOOK  — optional callback URL (Hermes cron trigger)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$SKILL_DIR/data/logs"
OUT_FILE="$LOG_DIR/firecrawl-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

cd "$SKILL_DIR"

echo "[$(date)] Starting firecrawl collector — args: $*" | tee "$OUT_FILE"

node scripts/firecrawl_collector.js "$@" 2>&1 | tee -a "$OUT_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo "[$(date)] Exited with code $EXIT_CODE" | tee -a "$OUT_FILE"

# If Hermes callback is configured, invoke it
if [[ -n "${HERMES_CALLBACK_URL:-}" ]]; then
  NEW_COUNT=$(wc -l < "$LOG_DIR"/firecrawl-$(date +%Y%m%d)-*.jsonl 2>/dev/null | awk '{sum+=$1} END{print sum+0}' || echo "0")
  curl -s -X POST "$HERMES_CALLBACK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"source\":\"firecrawl\",\"exit_code\":$EXIT_CODE,\"log\":\"$OUT_FILE\",\"new_reviews\":\"$NEW_COUNT\"}" \
    || true
fi

exit $EXIT_CODE