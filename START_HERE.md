# Start Here

If you are the orchestrator on a fresh GPU machine, do this in order.

## Mission

Your job is not to “train the best model.”

Your first-wave job is narrower:

`Identify the most promising training/data strategy for shaping recurrent hidden-state geometry for natural-language multi-hop reasoning under a 4xH100 budget.`

This is a signal hunt with strict gates.

## Read In This Order

1. `README.md`
2. `ORCHESTRATOR_RULES.md`
3. `docs/PRIOR_EXPERIMENT_FINDINGS.md`
4. `docs/CANONICAL_TESTING_METHODS.md`
5. `docs/H100_SETUP.md`
6. `docs/DEPENDENCIES_AND_SOURCES.md`
7. `docs/RESEARCH_SYNTHESIS.md`
8. `docs/MEASUREMENT_AND_GATES.md`
9. `docs/EXECUTION_PLAYBOOK.md`
10. `docs/COMMON_FAILURE_MODES.md`
11. `docs/HANDOFF.md`

Do not start setup until you have read at least through `docs/MEASUREMENT_AND_GATES.md`.

## Immediate Operating Rules

- Do not merge adapters into the base model.
- Do not start training before baseline gates pass.
- Do not trust low loss by itself.
- Do not use DACR-Bench as the primary first-wave go/no-go.
- Do not continue a checkpoint that fails output gates.
- Do not reuse stale probe artifacts.
- Do not improvise around failed gates.

## First Actions On A Fresh Machine

1. Clone this repo.
2. Run the machine bootstrap from `docs/H100_SETUP.md`.
3. Validate this repo:
   - `python3 scripts/validate_strategy_matrix.py`
   - `python3 scripts/preflight_check.py --root .`
4. Create the live private run repo:
   - `bash scripts/create_run_repo.sh botcoin-lt-run-$(date -u +%Y%m%d-%H%M)`
5. Move into the live run repo and commit immediately.
6. Start baseline setup and baseline gates only.

## What Success Looks Like

At the end of wave 1, you should have:

- a valid baseline anchor
- valid probe outputs
- valid benchmark outputs with parseable rates
- a ranked strategy matrix
- a clear next-step recommendation

## If You Feel Tempted To “Just Try Something”

Stop and re-read:

- `ORCHESTRATOR_RULES.md`
- `docs/COMMON_FAILURE_MODES.md`
- `docs/MEASUREMENT_AND_GATES.md`

The repo is designed so you do not have to improvise.

