# Canonical Testing Methods

This is the **canonical source of truth** for the first-wave testing methods.

If the orchestrator needs one file that says:

- what the actual experiment is
- which ideas from the two research passes survived
- which ideas were demoted
- what exact probes to run
- in what order
- with what thresholds
- and how to interpret results

this is that file.

If this file conflicts with other planning prose, use this file for the **testing methods**.

More specifically:

- use this file for exact method design
- use `docs/MEASUREMENT_AND_GATES.md` for validity and interpretation rules
- use `docs/EXECUTION_PLAYBOOK.md` for run sequencing and orchestration discipline
- use `configs/strategies/strategy_matrix.yaml` as a compact machine-readable summary, not the full method spec

## Scope

This file governs the first-wave `8xH100` signal hunt only when that hardware is available.

If only `4xH100` is available, the same methods still apply, but the wallclock schedule becomes looser.

It does **not** define second-wave scale-up or from-scratch looped model training.

## Precedence

The methods in this file are constructed from:

1. the strongest operational content from **Pass 2**
2. the strongest architectural framing from **Pass 1**
3. the distilled prior experiment findings
4. late-2025/2026 primary literature

Practical rule:

- **Pass 2 takes precedence for execution order, thresholds, and budgeting**
- **Pass 1 contributes architectural specificity where the exact design choice determines whether the operational test is scientifically valid**

## The Actual Question

The first wave is not trying to prove that latent reasoning is solved.

It is trying to answer:

`Which training/data strategy shows the strongest credible signal that structured recurrent-depth supervision can shape recurrent hidden-state geometry for natural-language multi-hop reasoning and causal reasoning under an 8xH100 first-wave budget, while keeping wallclock near 16 hours?`

## Transfer Ladder

The first wave is only useful if it clears the ladder in order:

1. scenario structural fidelity
2. real natural-language multi-hop transfer
3. causal reasoning transfer

Rule:

- a strategy can only be called a real transfer win if it improves the rung it targets without collapsing the rungs below it

## Why These Five Strategies

These are the five methods that survived the weighing process because they are the best combination of:

- evidence strength
- fit to structured-trace and natural-language reasoning data
- fit to a recurrent-depth base model
- cost under `8xH100` with a short wallclock target
- interpretability of outcomes

The five first-wave strategies are:

1. natural-language latent probe baseline
2. hop-aligned auxiliary supervision
3. dynamic recurrence plus hop curriculum
4. trajectory-classifier amplification
5. boundary-token format A/B

## Specification Tightening

The following points are pinned down here so they are **not** left to orchestrator discretion:

1. Strategy 1 uses **two distinct probes**, not one ambiguous probe family
2. Strategy 1 is judged by the **full AUC-by-depth curve**, not only monotone increase
3. Strategy 2 uses a **mid-sized auxiliary decoder**, not full coda and not tiny LoRA-only scaffolding
4. Strategy 2 uses **clean linear traces only** in wave 1 for step alignment
5. Strategy 3 requires **dynamic R during training**, not only an inference-time sweep
6. Strategy 5 Arm B uses **stable special-token initialization**

These are not optional refinements. They are part of the canonical method because they determine whether the result is interpretable.

## What Was Demoted

These are **not** first-wave priorities:

- full from-scratch Parcae rebuild
- large full-parameter continued pretraining
- pure latent RL as the first move

Reason:

- too expensive
- too hard to interpret
- too weakly supported relative to the first-wave alternatives

## Global Gates Before Any Strategy

Before training any variant, the base model must pass:

### Gate 1: Output Contract Smoke Test

Must produce answer-like outputs on:

- a simple completion prompt
- a short-answer DACR-style prompt

Reject if:

- prompt echo
- template continuation
- delimiter garbage
- non-answer continuation

### Gate 2: Standard Benchmark Smoke Test

Run a smoke eval on:

- HotpotQA
- DROP

Goal:

- validate usable outputs
- validate parseability

### Gate 3: Baseline Sanity Anchor

The baseline should roughly match the repaired anchor:

- HotpotQA `T=8`: about `8.0 EM / 13.9 F1`
- DROP `T=8`: about `17.2 EM / 21.0 F1`
- parseable rate: `100%`

Treat large deviation as an environment or evaluation-path problem.

## Probe Validity Rules

No probe is valid unless all are true:

1. current probe dataset
2. balanced enough labels
3. current hidden-state extraction path
4. intended recurrence depths actually captured
5. grouped or challenge-disjoint splitting where expected

If any fail, the probe is invalid.

## Canonical First-Wave Order

This is the canonical execution order:

### Phase A

1. baseline gates
2. Strategy 1 probe baseline

Why first:

- it is the measuring instrument for the rest
- it decides whether later strategies are trying to amplify existing structure or install missing structure

### Phase B

Run in parallel if resources permit:

- Strategy 3: dynamic recurrence plus hop curriculum
- Strategy 5: boundary-token A/B

Why:

- both are relatively decision-efficient
- Strategy 3 is the cleanest recurrence-aware transfer test
- Strategy 5 is the cheapest high-leverage data-format decision

### Phase C

Run after Phase B:

- Strategy 2: hop-aligned auxiliary supervision
- Strategy 4: trajectory-classifier amplification

Why:

- Strategy 2 is the strongest installed-structure bet but costs more
- Strategy 4 depends on the classifier gate and is best interpreted after the baseline probe story is known

## Canonical `8xH100` Wallclock Plan

The preferred first-wave rental target is:

- about `8xH100`
- about `16` wallclock hours
- not more than roughly `128 GPU-hours` unless a documented rerun is justified

This does **not** change the five strategies. It changes the spread of jobs, the concurrency, and when evaluation should start.

### Stage 0: bootstrap and baseline

Target wallclock:

- about `0.0` to `2.0` hours

Use:

- `2 GPUs` for baseline/output/benchmark anchor work
- remaining GPUs idle for training until the baseline gates pass

Reason:

- correctness still takes precedence over occupancy

### Stage 1: Strategy 1 probe baseline

Target wallclock:

- about `2.0` to `4.0` hours

Use:

- `2 GPUs` to accelerate extraction and probe computation
- remaining GPUs for non-training prep only

Reason:

- Strategy 1 still determines how to interpret the rest

### Stage 2: first parallel wave

Target wallclock:

- about `4.0` to `9.0` hours

Run concurrently:

- Strategy 3 on `2 GPUs`
- Strategy 5 Arm A on `2 GPUs`
- Strategy 5 Arm B on `2 GPUs`
- Strategy 4 classifier gate on `1 GPU`
- keep `1 GPU` available for output gates and early eval fan-out

Reason:

- Strategy 3 and 5 are the best decision-efficiency use of early parallelism
- Strategy 4 classifier gate is cheap enough to pull forward without changing the logic of the method

### Stage 3: second parallel wave

Target wallclock:

- about `9.0` to `14.0` hours

Run concurrently:

- Strategy 2 on `4 GPUs`
- Strategy 4 main training / reranking path on `2 GPUs`
- use `2 GPUs` for probes and external benchmarks on completed Phase B outputs

Reason:

- Strategy 2 is the strongest installed-structure method and benefits most from extra GPUs
- Strategy 4 is still comparatively cheap
- using free GPUs for eval prevents a long tail at the end of the rental

### Stage 4: closeout

Target wallclock:

- about `14.0` to `16.0` hours

Use all available GPUs for:

- remaining probe fan-out
- benchmark reruns needed for valid artifacts
- final result collection

The orchestrator should prefer a complete valid matrix over trying to squeeze in new unplanned experiments.

## Strategy 1: Natural-Language Latent Probe Baseline

### Why This Survived

Best combined logic from the two passes:

- Pass 2 was right that the baseline probe must come first and serve as the evaluation instrument for everything else.
- Pass 1 was right that downstream scores alone cannot answer whether useful latent structure is present.

Grounding:

- Lu-style results suggest weak or discontinuous **per-iteration token-level** latent step structure.
- trajectory-level latent credit assignment results suggest strong **trajectory-level** latent correctness signal exists.
- These are different probe families and must both be run to resolve the literature tension on natural-language multi-hop.

### Exact Method

Question:

`Does base recurrent depth already carry detectable natural-language multi-hop signal?`

Run:

- extract hidden states at recurrence depths `R in {4, 8, 16}`
- use `300` HotpotQA-style 2-hop examples with bridge signal where possible
- use `300` MuSiQue examples if available
- run **both** of the following probes:

#### Probe A: Lu-style per-iteration coda/logit-lens probe

- operate on a bridge-entity-relevant token position or equivalent question-end/bridge position
- decode per-iteration information from the recurrent state in a token-local way
- report per-depth token-level AUC or equivalent discriminative score

Question answered:

- `Is bridge-relevant information locally readable at individual recurrent steps?`

#### Probe B: Du-style pooled trajectory classifier

- pool the recurrent trajectory across depths and/or across the selected representation family
- train a simple linear or shallow classifier on the pooled trajectory representation
- report trajectory-level AUC by depth family or pooled setting

Question answered:

- `Does the full latent trajectory encode correctness-relevant multi-hop structure even if individual steps are noisy?`

These are intentionally different experiments. The disagreement between them is scientifically meaningful.

### Primary Metrics

- Lu-style per-iteration probe AUC by depth
- Du-style pooled trajectory probe AUC
- if the base probe is already strong, a small causal-suite sanity check can be added to test whether the signal survives beyond multi-hop

### Win Condition

- if **any** probe reaches roughly `AUC >= 0.65` at any depth, treat that as evidence that usable structure exists
- always report the **full AUC-by-depth curve**
- treat curve shape separately from peak value

### Interpretation

- high Lu-style and high Du-style signal: both local step structure and trajectory structure exist
- weak Lu-style but strong Du-style signal: trajectory structure exists, but per-step token-local structure is unstable or poorly localized
- non-monotonic curve with a clear early or mid-depth peak: structure exists but overthinking degrades it later
- flat low curve across both probes: little useful NL multi-hop structure is currently readable
- declining curve after an early peak: overthinking dominates at larger depths

### Budget

- about `6 GPU-hours`, but on `8xH100` it should complete in a much shorter wallclock slice because extraction and analysis can be parallelized

## Strategy 2: Hop-Aligned Auxiliary Supervision

### Why This Survived

Best combined logic from the two passes:

- Pass 1 correctly identified DACR step structure as a natural latent supervision scaffold.
- Pass 2 correctly converted that into the strongest concrete first-wave method.

Grounding:

- `SIM-CoT` is the strongest current evidence that step-level supervision stabilizes implicit/latent reasoning.
- prior findings already showed the collapse mode this strategy is meant to prevent

### Exact Method

Question:

`Can step-aligned latent supervision install stable hop-aware recurrent structure?`

Training setup:

- core-focused, conservative adaptation
- rank `8`
- dropout `0.1`
- LR around `1e-4`
- short first-wave token budget in the prior proven-safe regime

Data:

- DACR examples with at least `3` sequential extraction steps
- wave-1 filter to **clean linear chains only**
- include:
  - `direct_extraction`
  - simple `cross_section_synthesis`
- exclude for wave 1:
  - `trap_targeted`
  - `conditional_filtered`
  - obviously branching or unordered retrieval traces

Reason:

- wave-1 step supervision should be as close as possible to one-latent-step-to-one-reasoning-step alignment
- harder branching cases can return in wave 2 if the mechanism works on clean linear chains

Mechanism:

- attach an auxiliary decoder during training only
- supervise intermediate recurrent states against aligned DACR reasoning steps
- remove auxiliary head for inference

Auxiliary decoder size:

- use a **mid-sized auxiliary decoder**
- do **not** use the full coda as the auxiliary decoder
- do **not** reduce the auxiliary decoder to a tiny LoRA-only head
- canonical choice for wave 1: approximately **one transformer block at the base model width**

Reason:

- SIM-CoT-style evidence suggests very large auxiliary decoders can make the latent task too easy, reducing pressure on the recurrent core
- a tiny head risks under-capacity and noisy supervision
- a mid-sized decoder is the most defensible compromise for a `3.5B`-class base

### Primary Metrics

- bridge/entity probe improvement over Strategy 1 baseline
- auxiliary step prediction quality

### Behavioral Corroboration

- HotpotQA, MuSiQue, and DROP movement without collapse
- if available, a causal suite such as CausalQA or COPA should be checked without changing the prompt contract

### Win Condition

- meaningful probe improvement over Strategy 1 baseline
- plus evidence that step alignment is non-trivial
- ideally with some behavioral corroboration

### Interpretation

- positive: structured traces are useful as latent step teachers
- probe-only movement: structure shift without confirmed downstream benefit yet
- no movement: SIM-CoT-like transfer did not materialize at this scale

### Budget

- about `22 GPU-hours`; on `8xH100` this is the main candidate to spread across more GPUs in order to shrink wallclock

## Strategy 3: Dynamic Recurrence Plus Hop Curriculum

### Why This Survived

Best combined logic from the two passes:

- Pass 2 correctly elevated Kohli-style dynamic recurrence and curriculum as the best principled recurrence-aware recipe.
- Pass 1 correctly emphasized overthinking and depth extrapolation as central recurrent-depth problems.

Grounding:

- `Kohli 2026` is the key evidence
- recurrence-aware transfer should be judged by score-vs-depth behavior, not one fixed-depth score

### Exact Method

Question:

`Does recurrence-aware training improve behavior as inference depth increases?`

Training setup:

- conservative core-focused adaptation
- dynamic recurrence schedule during training
- curriculum bucketed by hop count
- measure across multiple inference depths after training

Data:

- DACR bucketed by hop complexity

Training-time recurrence rule:

- recurrence depth `R` must be sampled **during training**
- canonical form:
  - `R ~ clip(Poisson(lambda), R_min, R_max)` per training example
- vary `(lambda, R_min, R_max)` by curriculum stage

This is required. An inference-only `R` sweep on a fixed-`R`-trained model is **not** a valid execution of this strategy.

Eval:

- run benchmark sweeps across `R in {4, 8, 16, 32}` where feasible

### Primary Metric

- behavioral score by inference depth on multi-hop tasks, with a secondary causal-suite check where available

### Win Condition

- monotone or clearly favorable score scaling from lower to moderate recurrence depth on multi-hop tasks, without regressions on causal transfer checks

### Interpretation

- positive: recurrence-aware training transfers to natural-language multi-hop
- flat: recurrence-aware mechanism did not transfer
- decline: overthinking still dominates

### Budget

- about `18 GPU-hours`; on `8xH100` it belongs in the first parallel wave

## Strategy 4: Trajectory-Classifier Amplification

### Why This Survived

Best combined logic from the two passes:

- Pass 2 correctly preserved this as the main alternative to “install step structure.”
- Pass 1’s emphasis on latent geometry naturally supports a trajectory-level discrimination test.

Grounding:

- trajectory-level latent credit assignment work shows latent correctness signal may already exist
- raw attempts provide unusually good positive/negative same-task contrasts

### Exact Method

Question:

`Can existing latent correctness signal be amplified without being gamed?`

Phase A:

- train a trajectory classifier on DACR positive/negative pairs
- require a meaningful held-out AUC before proceeding

Phase B:

- train a conservative adapter using the trajectory classifier signal as an auxiliary preference signal

Phase C:

- re-measure classifier discrimination
- compare greedy vs reranked or guided selection on external behavior

### Primary Metrics

- classifier AUC before and after training
- reranked HotpotQA-style and causal-suite behavior

### Win Condition

- classifier remains discriminative
- guided selection or reranking yields meaningful lift on at least one external multi-hop benchmark, with causal transfer treated as a bonus check if the budget permits

### Interpretation

- positive: base latent signal existed and structured supervision sharpened it
- AUC collapse: classifier got gamed
- stable AUC with no behavioral lift: signal did not amplify usefully

### Budget

- about `20 GPU-hours`; on `8xH100` the classifier gate should be pulled forward into the first parallel wave

## Strategy 5: Boundary-Token Format A/B

### Why This Survived

Best combined logic from the two passes:

- Pass 1 was right that explicit step boundaries may help latent alignment.
- Pass 2 was right that this should be a controlled A/B, not a default assumption.

Grounding:

- step alignment logic from `SIM-CoT`
- prior collapse on structural-token patterns makes format changes high-risk and high-value

### Exact Method

Question:

`Do explicit hop boundaries help, hurt, or do nothing?`

Arm A:

- current DACR format

Arm B:

- DACR format with explicit hop-boundary tokens and explicit artifact boundaries

Keep matched:

- token budget
- optimizer
- recurrence schedule
- adaptation footprint

Special-token initialization:

- initialize new special-token embeddings as the **mean of existing vocabulary embeddings**

Reason:

- wave-1 token budgets are small enough that random initialization would confound the A/B by wasting too much budget on learning stable embeddings instead of testing the structure hypothesis

### Primary Metrics

- HotpotQA EM delta
- DROP EM delta
- if available, a causal-suite delta

### Secondary Metric

- probe AUC delta

### Win Condition

- treatment arm materially beats control on at least one external multi-hop benchmark, or shows a clear latent-structure win without behavioral loss; if the budget allows, a causal-suite sanity check should be included

### Interpretation

- positive: future structured data generation should include boundaries
- near-zero delta: current format is sufficient at this scale
- negative delta: boundaries likely increase harmful format overfitting

### Budget

- about `16 GPU-hours`; on `8xH100` the two A/B arms should each get dedicated parallel capacity

## Shared Evaluation Rules Across All Strategies

Every valid strategy result should include:

- post-train output gate result
- benchmark outputs with parseable rate
- probe outputs where applicable
- a note on whether the result moved scenario structural fidelity, real multi-hop transfer, causal transfer, or none
- findings entry with decision and rationale

Do not keep any checkpoint in the comparison set if:

- it fails output gates
- it shows obvious collapse
- it uses invalid or stale measurement artifacts

## Canonical Ranking Logic

At the end of wave 1, each strategy must be classified as one of:

- `strong positive`
- `weak positive`
- `informative negative`
- `invalid`

### Strong Positive

- probe moves
- behavior moves on at least one external multi-hop task
- depth behavior improves
- if a causal suite was run, it does not regress
- no collapse

### Weak Positive

- probe moves without clear behavior, or vice versa
- or multi-hop improves while the causal rung remains untested

### Informative Negative

- valid measurement shows no movement, gaming, or worsening

### Invalid

- stale data
- failed output gate
- missing parseable accounting
- wrong prompt contract
- interrupted result treated as complete

## Final First-Wave Recommendation Logic

Use this exact logic:

- if Strategy 2 wins: scale hop-aligned latent supervision first
- if Strategy 3 wins: scale recurrence-aware training and curriculum first
- if Strategy 4 wins: prioritize latent-signal amplification and reranking
- if Strategy 5 wins: change the structured data generation format before larger training
- if Strategy 1 shows no useful structure and the others fail: stop and revisit data/measurement before larger compute
- if a strategy improves scenario-only structure but not multi-hop transfer, do not count it as a scale-up win yet

## Resource-Use Rule

With `8xH100`, the orchestrator should try to keep all GPUs productive **after** the baseline gates pass.

But this does **not** justify:

- launching training before baseline validity
- skipping output gates
- overlapping phases in ways that make interpretation ambiguous

The point of `8xH100` is to reduce wallclock, not to weaken the scientific design.

## One-Sentence Mental Model

The first wave is:

`a tightly gated, evidence-ranked probe campaign using the strongest operational parts of Pass 2, sharpened by the best architectural insights from Pass 1, to decide which training method is worth scaling next.`
