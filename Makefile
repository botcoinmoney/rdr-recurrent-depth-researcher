PYTHON ?= python3
GPU_PROFILE ?=
GPU_COUNT ?=
GPU_RESERVE ?= 1
CHECKPOINT_MESSAGE ?= Checkpoint: $(shell date -u +%Y-%m-%dT%H:%MZ)

.PHONY: setup setup-auto setup-single setup-multi setup-cluster validate test preflight kickoff gpu-status gpu-allocate checkpoint demo-workspace

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip setuptools wheel && pip install -e ".[dev]"

setup-auto:
	$(PYTHON) scripts/setup_env.py --profile auto

setup-single:
	$(PYTHON) scripts/setup_env.py --profile single_gpu

setup-multi:
	$(PYTHON) scripts/setup_env.py --profile multi_gpu

setup-cluster:
	$(PYTHON) scripts/setup_env.py --profile cluster_shared

validate:
	$(PYTHON) scripts/validate_pipeline_config.py
	$(PYTHON) scripts/validate_strategy_matrix.py

test:
	$(PYTHON) -m pytest -q

preflight:
	$(PYTHON) scripts/preflight_check.py --root . $(if $(CHECK_GPU),--check-gpu,) $(if $(CHECK_TORCH),--check-torch,)

kickoff: validate
	$(MAKE) CHECK_GPU=1 CHECK_TORCH=1 preflight
	$(MAKE) gpu-status

gpu-status:
	$(PYTHON) scripts/gpu_status.py $(if $(GPU_PROFILE),--profile $(GPU_PROFILE),)

gpu-allocate:
	$(PYTHON) scripts/gpu_status.py $(if $(GPU_PROFILE),--profile $(GPU_PROFILE),) --allocate $(if $(GPU_COUNT),--count $(GPU_COUNT),) --reserve $(GPU_RESERVE)

checkpoint:
	bash scripts/checkpoint_commit_push.sh --message "$(CHECKPOINT_MESSAGE)"

demo-workspace:
	rdh init-workspace --workspace ./demo-workspace --force
	rdh run-cycle --workspace ./demo-workspace
