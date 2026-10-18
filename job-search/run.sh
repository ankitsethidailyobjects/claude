#!/usr/bin/env bash
# One-click start on macOS / Linux: ./run.sh
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "First run: setting up (takes a minute)…"
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
exec .venv/bin/streamlit run app.py
