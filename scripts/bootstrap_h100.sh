#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl wget tmux python3-venv build-essential

mkdir -p "${HOME}/.cache/huggingface" "${HOME}/venvs" "${HOME}/runs"

if [[ ! -d "${HOME}/venvs/botcoin-lt" ]]; then
  python3 -m venv "${HOME}/venvs/botcoin-lt"
fi

source "${HOME}/venvs/botcoin-lt/bin/activate"
python -m pip install --upgrade pip

cat <<'EOF'
Bootstrap complete.

Next:
1. export HF_HOME=$HOME/.cache/huggingface
2. export TRANSFORMERS_CACHE=$HOME/.cache/huggingface
3. clone the orchestrator repo
4. install the repo with pip install -e ".[dev]"
EOF

