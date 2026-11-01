#!/usr/bin/env bash
# Start theAIgency AI job market.  PORT defaults to 8503 (the Agent Library uses 8502).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8503}"
if [ ! -x .venv/bin/streamlit ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
exec .venv/bin/streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0
