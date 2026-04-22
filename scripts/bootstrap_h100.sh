#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl wget tmux python3-venv build-essential

mkdir -p /root/.cache/huggingface /root/venvs /root/runs

if [[ ! -d /root/venvs/botcoin-lt ]]; then
  python3 -m venv /root/venvs/botcoin-lt
fi

source /root/venvs/botcoin-lt/bin/activate
python -m pip install --upgrade pip

cat <<'EOF'
Bootstrap complete.

Next:
1. export HF_HOME=/root/.cache/huggingface
2. export TRANSFORMERS_CACHE=/root/.cache/huggingface
3. clone the orchestrator repo
4. install the repo with pip install -e ".[dev]"
EOF

