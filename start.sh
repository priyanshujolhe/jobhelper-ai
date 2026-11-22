#!/usr/bin/env bash
# JobHelper AI - One-Click Launcher
set -e
cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

python3 run.py
