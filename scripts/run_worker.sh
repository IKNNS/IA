#!/bin/sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$PROJECT_DIR"
exec python3 -m codex_worker --execute --watch --interval "${CODEX_WORKER_INTERVAL:-60}"
