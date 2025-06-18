#!/bin/bash

set -e

echo "🔎 Verificando se venv está instalado..."

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "⚙️ Instalando venv para Python $PY_VERSION..."
  sudo apt install -y python$PY_VERSION-venv
fi

if [ ! -d "venv" ]; then
  echo "🐍 Criando ambiente virtual..."
  python3 -m venv venv
fi

source venv/bin/activate

if ! command -v qpdf >/dev/null 2>&1; then
  echo "📦 Instalando qpdf..."
  sudo apt update || true
  sudo apt install -y qpdf
fi

echo "🚀 Executando script de junção de PDFs..."
python join.py

echo "✅ Finalizado! PDFs estão na pasta ./output"
