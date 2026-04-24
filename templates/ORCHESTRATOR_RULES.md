# Live Run Orchestrator Rules

## Mission

Run one valid experiment campaign with clear gates, clean logging, and correct restart behavior.

## Source Of Truth

For the actual first-wave method design and optimization requirements, use:

- `handoff/docs/CANONICAL_TESTING_METHODS.md`
- `handoff/docs/GPU_OPTIMIZATION_CHECKLIST.md`

If other prose in the live run repo conflicts with the handoff method spec, the handoff spec wins.

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
- do not start the main schedule until the GPU optimization checklist passes
- keep `findings.md`, `HANDOFF.md`, and the latest cycle report current without waiting for a human reminder
- refresh research and data catalogs when they are stale relative to the current loop objective
- prefer explicit benchmark and probe evidence over vibe-based selection of the next run
