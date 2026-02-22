#!/bin/bash
# XI-IO v8 INFINITY REHYDRATION SCRIPT
# Codename: The Cord Cutter (v28.3)

echo "--- ∞ XI-IO REHYDRATION START ∞ ---"

# 1. Framework Root Discovery
XI_ROOT=$(pwd)
echo "Establishing Root: $XI_ROOT"

# 2. Virtual Environment setup
if [ ! -d ".venv" ]; then
    echo "Creating Python Environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "Installing Dependencies..."
pip install -r requirements.txt

# 3. Ledger & State Preparation
echo "Preparing Industrial Ledger..."
mkdir -p ~/.xi-io
if [ ! -f ~/.xi-io/production_ledger.json ]; then
    echo "[]" > ~/.xi-io/production_ledger.json
fi

# 4. Neural Reality Check (Ollama)
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama detected. Verifying Neural State..."
    # Lazy pull models to ensure rehydration
    ollama pull xibalba:latest
    ollama pull llama3.1:8b
else
    echo "[!] WARNING: Ollama not found. Neural operations will be degraded."
fi

# 5. Environment Export
cat <<EOF > .env
XI_FRAMEWORK_ROOT=$XI_ROOT
XI_MODE=INDUSTRIAL
EOF

echo "--- ∞ REHYDRATION COMPLETE ∞ ---"
echo "Run: 'source .venv/bin/activate && python3 xi_cli.py asking where am i?' to verify."
