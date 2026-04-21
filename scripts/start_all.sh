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
GRADIO_HOST="${GRADIO_HOST:-0.0.0.0}"
GRADIO_PORT="${GRADIO_PORT:-7860}"

if [ "$API_RELOAD" = "1" ]; then
  "$VENV_PY" -m uvicorn api:app --host "$API_HOST" --port "$API_PORT" --reload &
else
  "$VENV_PY" -m uvicorn api:app --host "$API_HOST" --port "$API_PORT" &
fi
API_PID=$!

GRADIO_HOST="$GRADIO_HOST" GRADIO_PORT="$GRADIO_PORT" "$VENV_PY" gradio_app.py &
UI_PID=$!

cleanup() {
  kill "$API_PID" "$UI_PID" 2>/dev/null || true
  wait "$API_PID" "$UI_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Backend:  http://localhost:${API_PORT}"
echo "Frontend: http://localhost:${GRADIO_PORT}"

# macOS ships Bash 3.2 where `wait -n` is unavailable.
# Keep both processes running until one exits.
while kill -0 "$API_PID" 2>/dev/null && kill -0 "$UI_PID" 2>/dev/null; do
  sleep 1
done
