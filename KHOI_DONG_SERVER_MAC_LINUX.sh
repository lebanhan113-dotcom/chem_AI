#!/bin/sh
set -e
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
exec python -m uvicorn server:APP --host 127.0.0.1 --port 8000
