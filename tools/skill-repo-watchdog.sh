#!/usr/bin/env bash
set -euo pipefail
cd /opt/data/workspace/dgroch-skills
exec python3 tools/skill_repo_guard.py audit --fetch
