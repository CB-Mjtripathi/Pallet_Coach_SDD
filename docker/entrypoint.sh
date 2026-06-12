#!/bin/sh
set -eu

export PYTHONPATH=/app/scripts

python -m uvicorn pallet_coach.api.app:app --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

trap 'kill -TERM "$UVICORN_PID" "$NGINX_PID" 2>/dev/null || true' INT TERM

wait "$UVICORN_PID"
