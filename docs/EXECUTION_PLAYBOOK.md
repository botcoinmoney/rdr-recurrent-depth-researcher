# Execution Playbook

This is the end-to-end operational sequence for the orchestrator.

It assumes:

- fresh `8xH100` machine for the preferred short-wallclock plan
- this handoff repo is cloned
- a separate live private run repo will be created

If only `4xH100` is available, use the same phase order and same methods, but reduce concurrency and accept a longer wallclock.

## Phase 0: Bootstrap

1. complete `docs/H100_SETUP.md`
2. validate this handoff repo:
   - `python3 scripts/validate_strategy_matrix.py`
   - `python3 scripts/preflight_check.py --root .`
3. create the live run repo with:
   - `bash scripts/create_run_repo.sh <repo-name>`
4. move into the live run repo
5. validate the live run repo:
   - `python3 handoff/scripts/preflight_check.py --root .`
6. create the first commit

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
4. initialize the run manifest from `configs/run_manifest.yaml`
5. record the transfer ladder targets:
   - scenario structural fidelity
   - natural-language multi-hop transfer
   - causal reasoning transfer

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

### Phase 2B: Optimization readiness

Before the main first-wave schedule begins:

1. pass `docs/GPU_OPTIMIZATION_CHECKLIST.md`
2. record the planned GPU map in `findings.md`
3. record which capacity is reserved for output gates and eval
4. record the expected throughput bottleneck

Do not start the main schedule until this optimization checklist passes.

## Phase 3: Dataset Preparation

The orchestrator should distinguish between:

- training corpus
- probe corpus
- transfer-eval corpus
- benchmark corpus

The strategy family here assumes:

- clean structured positives for training
- balanced positive/negative examples for probes
- HotpotQA / DROP / MuSiQue-style external behavior checks for multi-hop transfer
- a causal suite when available for the final transfer rung

Before continuing:

1. record dataset sizes
2. record filtering rules
3. record any context-length exclusions
4. record challenge-disjoint or grouped split design
5. record which evaluation suites are being used for multi-hop transfer and causal transfer

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

### Canonical `8xH100` utilization plan

Target:

- finish the first wave in about `16` wallclock hours
- keep all 8 GPUs productive

Recommended GPU spread:

#### Phase A: baseline plus probe baseline

- GPU `0-1`: baseline smoke, baseline benchmark anchor, then Strategy 1 hidden-state extraction / probe work
- GPU `2-7`: dataset prep, model prefetch, and script validation on CPU until baseline gates pass; do not launch training early

#### Phase B: first parallel wave

- GPU `0-1`: Strategy 3 training
- GPU `2-3`: Strategy 5 Arm A
- GPU `4-5`: Strategy 5 Arm B
- GPU `6`: Strategy 4 classifier gate / trajectory-classifier Phase A
- GPU `7`: output gates and quick evals for jobs that finish first

#### Phase C: second parallel wave

- GPU `0-3`: Strategy 2 training
- GPU `4-5`: Strategy 4 training / reranking path
- GPU `6-7`: probe fan-out and external benchmark evals on completed Phase B variants

#### Phase D: wrap-up

- use all free GPUs for probes, benchmark reruns, and result aggregation fan-out

The orchestrator should prioritize keeping evaluation and output gates unblocked over rigidly preserving one exact GPU index.

### Fallback `4xH100` utilization plan

If only `4xH100` is available:

- keep `1 GPU` worth of capacity available for output gates, probes, or eval when possible
- run the same phase order
- prefer fewer concurrent jobs over ambiguous scheduling
- do not invent new methods or reorder the strategy precedence just because the machine is smaller

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
- multi-hop behavioral result
- causal result if measured
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

- if hop-aligned supervision wins, structured traces are likely useful as latent step teachers
- if dynamic-R wins, recurrence-aware training is the main missing ingredient
- if trajectory amplification wins, the recurrent-depth base already had useful structure and the current data mainly sharpens it
- if boundary A/B wins, future data generation should change
- if nothing wins, do not escalate to larger compute until the measurement story is fixed
- if a strategy improves scenario-only structure but not multi-hop transfer, do not count it as a scale-up win yet
