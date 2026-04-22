# Live Run Orchestrator Rules

## Mission

Run one valid experiment campaign with clear gates, clean logging, and correct restart behavior.

## Required Structure

- `findings.md` is the source of truth for runtime decisions
- each phase should leave artifacts behind before moving on
- invalid checkpoints do not proceed downstream

## Required Phase Order

1. setup and validation
2. baseline gates
3. strategy execution
4. probe and benchmark evaluation
5. ranking and decision

## Runtime Discipline

- wake on cadence
- avoid duplicate jobs
- do not run training before baseline gates pass
- do not weaken prompt/output gates for convenience

