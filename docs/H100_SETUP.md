# H100 Setup

This document is for a fresh `H100` Linux instance.

For the current repo, prefer the profile-driven bootstrap in [docs/RUNTIME_SETUP.md](/root/recurrent-depth-autoresearch-harness/docs/RUNTIME_SETUP.md) instead of hand-managing package versions.

Use this rule:

- if `8xH100` is available, use the canonical short-wallclock plan in this repo
- if only `4xH100` is available, use the same methods with a looser wallclock and reduced concurrency

The orchestrator should complete this setup before cloning or launching the live run repo.

## Goals

- install a stable Python environment
- confirm GPU visibility and BF16 support
- confirm `gh` and Hugging Face auth
- avoid stale or unstable cache paths
- prepare a clean workspace for the live experiment repo

## Required Tools

- Python `3.10+`
- `git`
- `gh`
- `tmux` or equivalent
- CUDA-enabled PyTorch

## Directory Layout

Recommended host layout:

```text
${HOME}/
├── recurrent-depth-autoresearch-harness/
├── runs/
│   └── <live-private-run-repo>/
├── .cache/
│   └── huggingface/
└── venvs/
    └── rdh/
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
python3 -m venv "$HOME/venvs/rdh"
. "$HOME/venvs/rdh/bin/activate"
python3 scripts/setup_env.py --profile h100_8gpu
```

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

- at least 4 visible GPUs
- no unexplained memory pressure before the run starts

Preferred result:

- 8 visible GPUs

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
git clone git@github.com:botcoinmoney/recurrent-depth-autoresearch-harness.git
cd recurrent-depth-autoresearch-harness
. "$HOME/venvs/rdh/bin/activate"
python3 scripts/validate_strategy_matrix.py
python3 scripts/preflight_check.py --root . --check-torch
```

## Create The Live Run Repo

Do not run the actual experiment directly in this handoff repo.

Create a fresh private run repo:

```bash
cd "$HOME/recurrent-depth-autoresearch-harness"
bash scripts/create_run_repo.sh rdh-run-$(date -u +%Y%m%d-%H%M)
```

This creates a separate repo under `$HOME/runs/` and bundles a `handoff/` snapshot into that live run repo so the run remains self-contained even if this handoff repo is not kept around.

## Protected Defaults

The orchestrator should keep these defaults unless a documented reason requires change:

- do not merge adapters
- on `8xH100`, keep at least one GPU available for output gates, probes, or eval fan-out when possible
- use isolated log directories
- log every material event
- push after each major phase

## Before Starting Real Jobs

Run:

```bash
cd "$HOME/runs/<live-run-repo>"
python3 handoff/scripts/preflight_check.py --root .
```

Proceed only if:

- auth works
- cache path is stable
- required docs exist
- findings log exists
- rules file exists

Before the main run begins, also pass `docs/GPU_OPTIMIZATION_CHECKLIST.md`.
