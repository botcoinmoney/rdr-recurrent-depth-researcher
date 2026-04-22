# Execution Playbook

This is the end-to-end operational sequence for the orchestrator.

It assumes:

- fresh `4xH100` machine
- this handoff repo is cloned
- a separate live private run repo will be created

## Phase 0: Bootstrap

1. complete `docs/H100_SETUP.md`
2. validate this handoff repo:
   - `python3 scripts/validate_strategy_matrix.py`
   - `python3 scripts/preflight_check.py --root .`
3. create the live run repo with:
   - `bash scripts/create_run_repo.sh <repo-name>`
4. move into the live run repo
5. create the first commit

## Phase 1: Live Run Repo Initialization

Inside the live run repo:

1. read:
   - `RULES.md`
   - `ORCHESTRATOR_RULES.md`
   - `findings.md`
2. create the first findings entry
3. write down:
   - machine type
   - CUDA visibility
   - auth status
   - cache path
   - target model
   - target datasets

Commit and push.

## Phase 2: Environment And Asset Validation

Before any expensive work:

1. verify auth:
   - `gh auth status`
   - `huggingface-cli whoami`
2. verify no unstable cache path is being used
3. prefetch the base model if necessary
4. verify benchmark and dataset access
5. verify no leftover experiment jobs are running

If any fail, stop and fix.

## Phase 3: Dataset Preparation

The orchestrator should distinguish between:

- training corpus
- probe corpus
- benchmark corpus

The strategy family here assumes:

- BOTCOIN/DACR clean positives for training
- balanced positive/negative examples for probes
- HotpotQA / DROP / MuSiQue-style external behavior checks

Before continuing:

1. record dataset sizes
2. record filtering rules
3. record any context-length exclusions
4. record challenge-disjoint or grouped split design

Commit and push.

## Phase 4: Baseline Gates

Do not train anything until baseline gates pass.

Required:

1. output contract smoke test
2. standard benchmark smoke test
3. baseline `T=8` benchmark run with parseable rate

The baseline artifact is the anchor for the whole decision matrix.

If baseline output or parseability is poor:

- stop
- debug the prompt/output contract
- rerun baseline

Do not launch training in parallel “to save time.”

## Phase 5: Strategy 1 First

Run the natural-language latent probe baseline first.

Why:

- it is the measuring instrument for the rest
- it decides whether the later story is “amplify existing structure” or “install missing structure”

Required outputs:

- per-depth probe metrics
- saved artifact paths
- findings entry interpreting whether depth helps, is flat, or hurts

Commit and push.

## Phase 6: First-Wave Training And Eval Order

Recommended order:

1. Strategy 3 and Strategy 5 in parallel if resources permit
2. Strategy 2 and Strategy 4 after the earlier phase completes

Reason:

- Strategy 3 and 5 are comparatively cheap and decision-efficient
- Strategy 2 is the strongest but more expensive installed-structure bet
- Strategy 4 depends on the latent classifier gate

## Phase 7: Per-Variant Required Sequence

For each variant:

1. launch training
2. monitor on cadence
3. inspect loss progression
4. run mandatory post-train output gate
5. if output gate fails, mark variant invalid
6. only passing variants proceed to probes or benchmarks

Then:

1. run the strategy-specific probe or classifier analysis
2. run behavioral evals
3. log results
4. commit and push

## Phase 8: Heartbeat / Watchdog Discipline

The orchestrator must not rely on chat memory alone.

Required:

- a heartbeat log
- periodic status writes
- explicit job ownership tracking
- duplicate-job prevention

If a watchdog script is used, it must:

- refuse duplicate instances
- detect already-running jobs
- treat existing valid artifacts as complete
- never restart a completed benchmark just because local state went stale

## Phase 9: End-Of-Wave Decision

At the end, produce a matrix with:

- strategy
- status
- probe result
- behavioral result
- depth result
- failure modes
- recommendation

Then classify the next step as one of:

1. scale the winning retrofit strategy
2. rerun the strongest weak-positive at higher token budget
3. pivot to elastic-depth or more explicit recurrence-aware training
4. stop and revisit data or measurement before spending more

## Recommended First-Wave Interpretation

Use this prior when scores are ambiguous:

- if hop-aligned supervision wins, BOTCOIN traces are likely useful as latent step teachers
- if dynamic-R wins, recurrence-aware training is the main missing ingredient
- if trajectory amplification wins, Huginn already had structure and BOTCOIN data mainly sharpens it
- if boundary A/B wins, future BOTCOIN data generation should change
- if nothing wins, do not escalate to larger compute until the measurement story is fixed

