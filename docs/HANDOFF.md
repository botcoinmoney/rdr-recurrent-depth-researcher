# Handoff

This document is for the orchestrator receiving this repository on a fresh machine.

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

`Which of the five probe strategies shows the strongest credible positive signal that BOTCOIN-style multi-hop traces can shape recurrent hidden-state geometry for natural-language reasoning under a 4xH100 budget?`

## The Main Framing Corrections

Carry these forward into every decision:

1. previous local experiment history showed that invalid measurement paths can create false confidence
2. low loss can indicate memorization rather than learning
3. output gates matter as much as train loss
4. DACR-Bench can be misleading early if the prompt/output contract is not aligned
5. strategy ranking matters more than any single raw score

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
4. commit the starting state in that live repo
5. start the baseline gates

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
- a recommended next move

