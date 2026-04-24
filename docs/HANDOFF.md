# Handoff

This document is for the orchestrator receiving this repository on a fresh machine.

Nothing in the intended operating flow should depend on access to the original development workspace. The pertinent prior findings and framing corrections are bundled into this repository.

## What This Repo Is

This repo is a **standalone orchestration package**.

It is designed to be cloned, validated, and then used to create a **separate live private run repo** for the actual experiment.

## What This Repo Is Not

It is not:

- the final training stack
- a claim that recurrent-depth latent reasoning is solved
- a replacement for disciplined live run logging

## The Narrow Question

The first wave is trying to answer:

`Which of the five probe strategies shows the strongest credible positive signal that structured recurrent-depth supervision can shape recurrent hidden-state geometry for natural-language multi-hop reasoning and causal reasoning under an 8xH100 first-wave budget, while keeping wallclock near 16 hours?`

## The Main Framing Corrections

Carry these forward into every decision:

1. prior experiment history, as distilled in `docs/PRIOR_EXPERIMENT_FINDINGS.md`, showed that invalid measurement paths can create false confidence
2. low loss can indicate memorization rather than learning
3. output gates matter as much as train loss
4. narrow task-specific benchmarks can be misleading early if the prompt/output contract is not aligned
5. strategy ranking matters more than any single raw score
6. scenario-only structure is not enough unless it transfers to real tasks

## The Five First-Wave Strategies

1. natural-language latent probe baseline
2. hop-aligned auxiliary supervision
3. dynamic recurrence plus hop curriculum
4. trajectory-classifier amplification
5. boundary-token A/B

Read `docs/RESEARCH_SYNTHESIS.md` for why these survived the weighing process.

## What To Do First On A New Machine

1. follow `docs/H100_SETUP.md`
2. validate this repo
3. create the live private run repo
4. confirm the live run repo contains the bundled `handoff/` directory with docs/configs/scripts
5. run `python3 handoff/scripts/preflight_check.py --root .` inside the live run repo
6. commit the starting state in that live repo
7. start the baseline gates

## What To Never Do

- never merge adapters into the base model
- never skip findings logging
- never keep a failed-output checkpoint in the comparison set
- never downgrade validity standards to keep the cluster busy
- never claim success from one benchmark or one probe

## Expected Deliverables At The End Of Wave 1

- a findings log with timestamps and decisions
- benchmark artifacts with parseable rates
- probe artifacts for valid variants
- a ranked strategy matrix
- a filled run manifest with the transfer ladder outcome
- a recommended next move
