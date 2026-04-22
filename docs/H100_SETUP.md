# 4xH100 Setup

This document is for a fresh `4xH100` Linux instance.

The orchestrator should complete this setup before cloning or launching the live run repo.

## Goals

- install a stable Python environment
- confirm GPU visibility and BF16 support
- confirm `gh` and Hugging Face auth
- avoid stale or unstable cache paths
- prepare a clean workspace for the live experiment repo

## Required Tools

- Python `3.11+`
- `git`
- `gh`
- `tmux` or equivalent
- CUDA-enabled PyTorch

## Directory Layout

Recommended host layout:

```text
${HOME}/
├── botcoin-latent-reasoning-orchestrator/
├── runs/
│   └── <live-private-run-repo>/
├── .cache/
│   └── huggingface/
└── venvs/
    └── botcoin-lt/
```

Do not place Hugging Face caches on unstable network mounts if a local disk path is available.

Recommended:

- `HF_HOME=$HOME/.cache/huggingface`
- `TRANSFORMERS_CACHE=$HOME/.cache/huggingface`

## Machine Bootstrap

```bash
sudo apt-get update
sudo apt-get install -y git curl wget tmux python3-venv build-essential
python3 --version
nvidia-smi
gh --version
```

## Auth

```bash
gh auth status
```

If needed:

```bash
gh auth login
```

For Hugging Face:

```bash
huggingface-cli whoami
```

If needed:

```bash
huggingface-cli login
```

## Python Environment

```bash
mkdir -p "$HOME/venvs"
python3 -m venv "$HOME/venvs/botcoin-lt"
. "$HOME/venvs/botcoin-lt/bin/activate"
python -m pip install --upgrade pip
```

Then install repo requirements from this handoff package or the live run repo.

## GPU Sanity Checks

```bash
nvidia-smi
python - <<'PY'
import torch
print("cuda_available", torch.cuda.is_available())
print("device_count", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))
PY
```

Minimum expected result:

- 4 visible GPUs
- no unexplained memory pressure before the run starts

## Stable Cache Path

Export these in the shell profile used by the orchestrator:

```bash
export HF_HOME="$HOME/.cache/huggingface"
export TRANSFORMERS_CACHE="$HOME/.cache/huggingface"
export HUGGINGFACE_HUB_CACHE="$HOME/.cache/huggingface"
```

This is mandatory if the machine has shown unstable or remote-cache behavior before.

## Clone The Handoff Repo

```bash
cd "$HOME"
git clone git@github.com:botcoinmoney/botcoin-latent-reasoning-orchestrator.git
cd botcoin-latent-reasoning-orchestrator
. "$HOME/venvs/botcoin-lt/bin/activate"
pip install -e ".[dev]"
python3 scripts/validate_strategy_matrix.py
python3 scripts/preflight_check.py --root .
```

## Create The Live Run Repo

Do not run the actual experiment directly in this handoff repo.

Create a fresh private run repo:

```bash
cd "$HOME/botcoin-latent-reasoning-orchestrator"
bash scripts/create_run_repo.sh botcoin-lt-run-$(date -u +%Y%m%d-%H%M)
```

This creates a separate repo under `$HOME/runs/` and bundles a `handoff/` snapshot into that live run repo so the run remains self-contained even if this handoff repo is not kept around.

## Protected Defaults

The orchestrator should keep these defaults unless a documented reason requires change:

- do not merge adapters
- keep GPU 0 free for output gates or eval when possible
- use isolated log directories
- log every material event
- push after each major phase

## Before Starting Real Jobs

Run:

```bash
python3 scripts/preflight_check.py --root "$HOME/runs/<live-run-repo>"
```

Proceed only if:

- auth works
- cache path is stable
- required docs exist
- findings log exists
- rules file exists

