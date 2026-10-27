#!/bin/sh
set -eu
: "${EDUPLAN_DATA_DIR:=/data}"
mkdir -p "$EDUPLAN_DATA_DIR"
chown edupuser:edupuser "$EDUPLAN_DATA_DIR"
if [ -z "${EDUPLAN_ADMIN_PASSWORD:-}" ]; then
  echo 'ERROR: Set EDUPLAN_ADMIN_PASSWORD in the hosting environment (16+ chars).' >&2
  exit 1
fi
exec gosu edupuser uvicorn server:app --host 0.0.0.0 --port "${PORT:-10000}" --workers 1 --proxy-headers
