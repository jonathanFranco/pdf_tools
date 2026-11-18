#!/bin/bash
set -e

if ! command -v qpdf >/dev/null 2>&1; then
  echo "📦 Installing qpdf..."
  sudo apt update || true
  sudo apt install -y qpdf
fi

exec python3 "$(dirname "$0")/main.py" "$@"
