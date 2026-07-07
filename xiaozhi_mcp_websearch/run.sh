#!/usr/bin/env sh
set -eu

CONFIG_PATH="${XIAOZHI_WEBSEARCH_CONFIG:-/data/options.json}"

python - <<'PY'
from app.config import load_config
from app.security import sanitize_log_value

settings = load_config()
print("Xiaozhi MCP WebSearch configuration:")
print(sanitize_log_value(settings.safe_summary()))
PY

exec python -m app.main

