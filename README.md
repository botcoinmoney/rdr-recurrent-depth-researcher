# BOTCOIN Latent Reasoning Orchestrator

This repository is a standalone handoff package for running a BOTCOIN recurrent-depth transformer signal hunt on a fresh `4xH100` instance.

Its purpose is not to be the training stack itself. Its purpose is to make the orchestrator safe, disciplined, and reproducible:

- set up the machine correctly
- create a separate private run repo for the live experiment
- enforce gates before burning GPU time
- run the highest-value first-wave experiments in the right order
- log findings, heartbeat checks, and decisions continuously
- avoid known failure modes such as adapter merge, stale probes, invalid prompt contracts, and mode collapse

## What This Package Contains

- `ORCHESTRATOR_RULES.md`: non-negotiable run discipline
- `RULES.md`: top-level experiment philosophy and safety constraints
- `docs/`: full end-to-end execution guide, research synthesis, setup, measurement, and handoff docs
- `configs/`: environment, thresholds, and first-wave strategy definitions
- `templates/`: starting files for the live per-run private repo
- `scripts/`: bootstrap, preflight, validation, run-repo creation, and heartbeat helpers
- `tests/`: lightweight contract tests so the scaffolding fails closed

## Research Position

The repo is intentionally opinionated.

For a `4xH100` first wave, the best current bet is **not** a large from-scratch looped model build. The best bet is a tightly gated **signal hunt** around a strong recurrent-depth base model, BOTCOIN/DACR-style data, and five specific probes:

1. natural-language latent probe baseline
2. hop-aligned auxiliary supervision
3. dynamic recurrence plus hop curriculum
4. trajectory-classifier amplification
5. boundary-token A/B data test

The late-2025/2026 architectural work that most matters for second-wave scaling is:

- `ETD` for selective recurrent retrofitting
- `LoopFormer` for elastic-depth training
- `Parcae` for stable from-scratch looped models
- `SIM-CoT` for step-aligned latent supervision
- `LTO` for latent trajectory reward modeling

The repo folds those ideas into a practical execution order rather than chasing all of them at once.

## Fast Start

```bash
git clone git@github.com:botcoinmoney/botcoin-latent-reasoning-orchestrator.git
cd botcoin-latent-reasoning-orchestrator
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
python3 scripts/validate_strategy_matrix.py
python3 scripts/preflight_check.py --root .
```

Then read, in order:

1. `ORCHESTRATOR_RULES.md`
2. `docs/H100_SETUP.md`
3. `docs/RESEARCH_SYNTHESIS.md`
4. `docs/E2E_PIPELINE.md`
5. `docs/EXECUTION_PLAYBOOK.md`
6. `docs/MEASUREMENT_AND_GATES.md`
7. `docs/HANDOFF.md`

## Required Orchestrator Behavior

Before any real run:

1. Create a new private GitHub repo for the live experiment.
2. Copy in the templates from `templates/`.
3. Commit immediately.
4. Use that run repo, not this handoff repo, for live logs, code changes, and experiment artifacts.

Use:

```bash
bash scripts/create_run_repo.sh botcoin-lt-run-YYYYMMDD
```

## Hard Safety Constraints

- Never merge LoRA adapters into the base model.
- Never start training before the baseline output gate and benchmark smoke gate pass.
- Never trust DACR-Bench alone as the primary go/no-go.
- Never keep training past collapse indicators just because GPUs are allocated.
- Never reuse stale probe artifacts after code or data-path changes.
- Never treat one benchmark number as success.

## Validation

```bash
make validate
make test
```

## Intended Outcome

At the end of a first wave, the orchestrator should produce:

- one ranked matrix of the five strategies
- probe deltas across depth
- benchmark deltas with parseable rates
- a clear go/no-go decision for scale-up
- a written rationale for the next most defensible training investment

