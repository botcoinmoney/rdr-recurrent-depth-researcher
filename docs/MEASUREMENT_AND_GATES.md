# Measurement And Gates

This document defines what counts as a valid result.

If the orchestrator weakens these gates, the experiment stops being interpretable.

## First-Wave Measurement Stack

The first wave depends on three evidence classes:

1. baseline and post-train behavior on external benchmarks
2. latent-space probe movement across recurrence depth
3. variant-to-variant comparison under matched budgets

No single class is sufficient alone.

## Baseline Gates

Before training any variant, the base model must pass:

### Gate A: Output contract smoke test

The baseline must produce answer-like outputs on:

- a simple completion prompt
- a short-answer DACR-style prompt

Reject if:

- prompt echo
- template continuation instead of answering
- delimiter garbage
- non-answer continuation

### Gate B: Standard benchmark smoke test

Run a small smoke evaluation on:

- HotpotQA
- DROP

The point is not score quality yet. The point is usable outputs and parseability.

### Gate C: Baseline benchmark sanity

For the main first wave, the baseline should roughly match the known repaired numbers:

- HotpotQA `T=8`: about `8.0 EM / 13.9 F1`
- DROP `T=8`: about `17.2 EM / 21.0 F1`
- parseable rate: `100%`

Treat `±2` points on a small smoke set as acceptable drift. Larger drift means the environment, prompt path, or model path changed.

## Probe Validity Gates

Probe claims are valid only if all are true:

1. current probe dataset is used
2. labels are balanced enough for meaningful discrimination
3. hidden-state extraction uses the current code path
4. intended recurrence depths are actually captured
5. grouped or challenge-disjoint splitting is used where the probe design expects it

If any of these fail, the probe is invalid.

## Behavioral Reporting Requirements

Each benchmark artifact must include:

- benchmark name
- recurrence depth
- sample count
- total outputs
- parseable outputs
- parseable rate
- score metric(s)

Without parseable rate, keep the artifact but do not use it as decision evidence.

## Collapse Indicators

Stop a variant if one or more appear clearly:

- training loss falls into an implausibly low memorization regime for the data size
- outputs become repetitive or delimiter-heavy
- output gate fails after training
- benchmark behavior craters relative to baseline

Examples of suspicious patterns:

- repeated `}` or `>`
- repetitive restatement loops
- simple completion passes but DACR-style answer prompt fails badly

## Strategy-Specific Win Conditions

### Strategy 1: NL probe baseline

Primary question:

`Is there detectable latent multi-hop signal in the base model?`

Win signal:

- probe AUC improves with depth by a material amount

Negative but useful signal:

- flat or declining AUC with depth

### Strategy 2: Hop-aligned auxiliary supervision

Primary question:

`Does step-level latent supervision install measurable hop-aligned structure?`

Require:

- improved bridge/entity or analogous probe signal
- some behavioral corroboration or at least no collapse

### Strategy 3: Dynamic-R plus curriculum

Primary question:

`Does recurrence-aware training improve score as inference depth increases?`

Require:

- monotone or materially positive score-vs-depth behavior

### Strategy 4: Trajectory-classifier amplification

Primary question:

`Can an existing latent correctness signal be amplified without being gamed?`

Require:

- classifier remains discriminative
- reranking or guided sampling produces a measurable lift

### Strategy 5: Boundary-token A/B

Primary question:

`Do explicit hop boundaries help, hurt, or do nothing?`

Require:

- A/B delta on matched runs

## Decision Logic

Interpret outcomes with the following hierarchy:

### Strong positive

- probe signal moves
- benchmark signal moves
- depth behavior becomes more favorable
- no collapse or invalidation

### Weak positive

- probe moves but behavior does not
- or behavior moves but probe remains ambiguous

### Informative negative

- no movement despite valid measurement
- classifier gets gamed
- depth scaling worsens
- boundary tokens hurt generalization

### Invalid

- stale dataset
- failed output gate
- missing parseable accounting
- wrong prompt contract
- interrupted or partial artifact treated as complete

## What To Report At The End

The final summary for each strategy should have:

- status: `strong positive`, `weak positive`, `informative negative`, or `invalid`
- evidence:
  - probe
  - behavior
  - depth
- recommended next action:
  - scale
  - rerun at higher token budget
  - demote
  - stop

