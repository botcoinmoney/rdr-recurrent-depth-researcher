# Experiment Rules

This repository exists to keep the orchestrator on the correct path.

The orchestrator is not allowed to improvise around failed gates, stale measurements, or setup problems. If something breaks, fix the real issue and continue on the intended path.

## Core Principles

1. Correctness over speed.
2. Scientific validity over apparent progress.
3. Clean negative results are valuable.
4. One invalid benchmark or probe can poison the whole run.
5. Adapter safety, logging discipline, and restartability matter as much as model quality.

## Non-Negotiable Behavior

1. Never merge LoRA or adapter weights into the base model.
2. Never run training before baseline output and benchmark gates pass.
3. Never continue a run after clear collapse indicators just because GPUs are already rented.
4. Never reuse stale probe artifacts after changing code, data filtering, prompt contracts, or hidden-state extraction logic.
5. Never accept a result without parseable-rate accounting when output formatting matters.
6. Never let a narrow task-specific benchmark override stronger evidence from standard benchmarks if the prompt/output contract is still unstable.
7. Never scale from a single positive metric. Require convergence of probe, behavior, and depth evidence.

## Repo Separation

This repository is the handoff package.

Every real GPU run must happen in a separate private run repository created from the templates here. That run repository is where the orchestrator writes:

- `findings.md`
- run-specific rules
- commits
- logs
- local patches
- benchmark summaries

This package should remain stable and reusable.

## Evidence Hierarchy

Rank evidence in this order:

1. validated probe and benchmark artifacts from the current run
2. repaired findings from prior runs that survived postmortem review
3. late-2025/2026 primary papers
4. rough exploratory notes

If rough notes conflict with repaired artifacts or primary papers, the rough notes lose.

## Default Goal

The first wave is a signal hunt, not a productization run and not a claim of solved latent reasoning.

The actual question is:

`Which training, data, and evaluation strategy shows the strongest credible evidence of durable recurrent-depth improvement on the current scenario, under the available compute budget, while preserving valid controls and reproducible measurement?`
