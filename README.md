# BOTCOIN Latent Reasoning Orchestrator

This repository is a standalone handoff package for running a BOTCOIN recurrent-depth transformer signal hunt on a fresh `4xH100` instance.

It is intended to be **self-contained for a fresh machine**. The orchestrator should not need access to the original BOTCOIN workspace or this current system to understand the plan, the prior findings, or the guardrails.

Its purpose is not to be the training stack itself. Its purpose is to make the orchestrator safe, disciplined, and reproducible:

- set up the machine correctly
- create a separate private run repo for the live experiment
- enforce gates before burning GPU time
- run the highest-value first-wave experiments in the right order
- log findings, heartbeat checks, and decisions continuously
- avoid known failure modes such as adapter merge, stale probes, invalid prompt contracts, and mode collapse

## What This Package Contains

- `START_HERE.md`: the single entrypoint for a fresh orchestrator
- `ORCHESTRATOR_RULES.md`: non-negotiable run discipline
- `RULES.md`: top-level experiment philosophy and safety constraints
- `docs/`: full end-to-end execution guide, research synthesis, setup, measurement, and handoff docs
- `docs/CANONICAL_TESTING_METHODS.md`: the single canonical testing-methods file reconstructed from the two research passes
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

1. `START_HERE.md`
2. `ORCHESTRATOR_RULES.md`
3. `docs/H100_SETUP.md`
4. `docs/PRIOR_EXPERIMENT_FINDINGS.md`
5. `docs/CANONICAL_TESTING_METHODS.md`
6. `docs/DEPENDENCIES_AND_SOURCES.md`
7. `docs/RESEARCH_SYNTHESIS.md`
8. `docs/E2E_PIPELINE.md`
9. `docs/EXECUTION_PLAYBOOK.md`
10. `docs/MEASUREMENT_AND_GATES.md`
11. `docs/COMMON_FAILURE_MODES.md`
12. `docs/HANDOFF.md`

## Required Orchestrator Behavior

Before any real run:

1. Create a new private GitHub repo for the live experiment.
2. Copy in the templates from `templates/`.
3. Copy the bundled `handoff/` snapshot into that run repo so it remains self-contained after handoff.
4. Commit immediately.
5. Use that run repo, not this handoff repo, for live logs, code changes, and experiment artifacts.

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

