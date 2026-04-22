# Live Experiment Run Repo

This is the live private run repository for a BOTCOIN latent-reasoning signal hunt.

It was created from the standalone handoff package and is the canonical place for:

- `findings.md`
- live code edits
- logs
- benchmark summaries
- probe outputs
- run-specific docs

It should also contain a bundled `handoff/` directory copied from the standalone handoff repo so the live run remains self-contained on a fresh machine.

## Purpose

Track one concrete experiment campaign cleanly and reproducibly.

## Hard Rules

- never merge adapters into the base model
- never skip baseline gates
- never continue a failed-output checkpoint into probes or benchmarks
- commit and push after every major phase

## Required Reading

1. `RULES.md`
2. `ORCHESTRATOR_RULES.md`
3. `handoff/docs/PRIOR_EXPERIMENT_FINDINGS.md`
4. `handoff/docs/RESEARCH_SYNTHESIS.md`
5. `findings.md`

