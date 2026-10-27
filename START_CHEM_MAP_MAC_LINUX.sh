#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
export CHEMMAP_DEMO=1
printf 'CHEM-MAP TUTOR AI V7.2: open http://127.0.0.1:8080/\n'
node server/server.js
