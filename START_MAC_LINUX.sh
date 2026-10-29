#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  printf '%s\n' 'Edit .env with Gemini API key, Google Cloud settings and APP_ACCESS_TOKEN; then rerun.'
  exit 0
fi
printf 'Open http://localhost:8000/index.html\n'
python server.py
