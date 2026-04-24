#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git curl wget tmux python3-venv build-essential

mkdir -p "${HOME}/.cache/huggingface" "${HOME}/venvs" "${HOME}/runs"

if [[ ! -d "${HOME}/venvs/rdh" ]]; then
  python3 -m venv "${HOME}/venvs/rdh"
fi

source "${HOME}/venvs/rdh/bin/activate"
python -m pip install --upgrade pip setuptools wheel

cat <<'EOF'
Bootstrap complete.

Next:
1. export HF_HOME=$HOME/.cache/huggingface
2. export TRANSFORMERS_CACHE=$HOME/.cache/huggingface
3. export HUGGINGFACE_HUB_CACHE=$HOME/.cache/huggingface
4. clone the orchestrator repo
5. install the repo with pip install -e ".[dev]"
6. run make kickoff once the repo is cloned
EOF
