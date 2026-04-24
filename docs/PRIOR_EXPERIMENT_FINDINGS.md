# Prior Experiment Findings

This document distills the pertinent lessons from earlier recurrent-depth experiment work so the orchestrator does **not** need access to the original machine or workspace.

Everything here is included because it materially changes how a fresh run should be executed.

## What Was Learned

### 1. Invalid measurement paths created false confidence

Earlier orchestration mixed phases, used stale probe assumptions, and trusted incomplete results too early.

Key correction:

- do not trust probe movement unless the dataset, hidden-state extraction path, split logic, and recurrence capture path are all current and explicitly validated

Implication for the fresh orchestrator:

- baseline and probe validation are not optional setup chores; they are the core of experiment correctness

### 2. Low loss was often a bad sign, not a good one

Observed failure mode:

- expressive LoRA plus too much training on a small dataset drove the model into memorization
- outputs degraded into delimiter garbage, repetition, or broken reasoning-format behavior

Implication:

- do not optimize for lowest training loss
- monitor for collapse patterns
- prefer conservative rank and token budgets in first-wave probes

### 3. Output gates were more trustworthy than train loss

A checkpoint could look healthy by train loss and still fail badly at generation time.

Observed failure modes included:

- prompt echo
- repetitive answer templates
- normal simple completion but broken structured reasoning output

Implication:

- every post-train checkpoint must pass an output gate before probes or benchmarks

### 4. Full-model adaptation was riskier than core-focused adaptation

Earlier evidence suggested:

- full-LoRA could appear competitive by loss while degrading output behavior
- core-focused low-rank adaptation was a safer first-wave bet

Implication:

- keep a recurrent-core-focused strategy in the first wave
- do not assume broader adaptation means better latent reasoning

### 5. Small, conservative runs produced the only credible early positive signal

The strongest repaired positive signal came from a minimal regime:

- low LoRA rank
- short token budget
- high-loss, non-collapsed stopping point
- core-only adaptation

Implication:

- the first wave should be a signal hunt, not an aggressive optimization campaign

### 6. A narrow task-specific benchmark alone was not a safe early go/no-go

Why:

- prompt/output formatting can dominate the score
- a model can fail a strict format contract without proving the underlying reasoning signal is absent

Implication:

- use standard benchmarks like HotpotQA and DROP as primary early behavior checks
- treat any narrow format-sensitive benchmark as secondary until the prompt/output contract is proven stable

### 7. The training corpus and probe corpus must be handled differently

Fresh-run design should preserve this split:

- training: clean positive traces
- probes: balanced positive/negative examples with discriminative labels

Implication:

- do not treat “the dataset” as a single undifferentiated artifact

### 8. Challenge-disjoint or grouped splitting matters

Earlier probe overconfidence risk came from weak separation logic.

Implication:

- grouped or challenge-disjoint splits should be used whenever the probe design expects them

## Baseline Anchor Values

These numbers are not sacred, but they are the repaired anchor the fresh orchestrator should use as a sanity target before training:

- HotpotQA at `T=8`: about `8.0 EM / 13.9 F1`
- DROP at `T=8`: about `17.2 EM / 21.0 F1`
- parseable rate: `100%`

Interpretation:

- if a fresh environment is far away from these on the same model/prompt path, the environment or evaluation path changed

## What This Means For The Fresh Run

The orchestrator should behave as if the prior experiment already paid for several expensive mistakes:

1. stale measurement
2. collapse by overtraining
3. trusting train loss too much
4. allowing invalid checkpoints downstream
5. letting format issues dominate interpretation

The value of this handoff package is that those lessons are now bundled here, rather than being trapped on the original machine.
