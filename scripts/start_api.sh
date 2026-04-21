#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

VENV_PY="$ROOT_DIR/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "Missing virtualenv at .venv. Run: make setup"
  exit 1
fi

API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
API_RELOAD="${API_RELOAD:-0}"

if [ "$API_RELOAD" = "1" ]; then
  "$VENV_PY" -m uvicorn api:app --host "$API_HOST" --port "$API_PORT" --reload
else
  "$VENV_PY" -m uvicorn api:app --host "$API_HOST" --port "$API_PORT"
fi
