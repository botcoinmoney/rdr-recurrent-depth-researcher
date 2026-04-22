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

## Scope

This file governs the first-wave `4xH100` signal hunt only.

It does **not** define second-wave scale-up or from-scratch looped model training.

## Precedence

The methods in this file are constructed from:

1. the strongest operational content from **Pass 2**
2. the strongest architectural framing from **Pass 1**
3. the distilled prior experiment findings
4. late-2025/2026 primary literature

Practical rule:

- **Pass 2 takes precedence for execution order, thresholds, and budgeting**
- **Pass 1 contributes architectural interpretation and demotion logic**

## The Actual Question

The first wave is not trying to prove that latent reasoning is solved.

It is trying to answer:

`Which training/data strategy shows the strongest credible signal that BOTCOIN-style multi-hop traces can shape recurrent hidden-state geometry for natural-language reasoning under a 4xH100 budget?`

## Why These Five Strategies

These are the five methods that survived the weighing process because they are the best combination of:

- evidence strength
- fit to BOTCOIN/DACR data
- fit to a recurrent-depth base model
- cost under `4xH100`
- interpretability of outcomes

The five first-wave strategies are:

1. natural-language latent probe baseline
2. hop-aligned auxiliary supervision
3. dynamic recurrence plus hop curriculum
4. trajectory-classifier amplification
5. boundary-token format A/B

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

## Strategy 1: Natural-Language Latent Probe Baseline

### Why This Survived

Best combined logic from the two passes:

- Pass 2 was right that the baseline probe must come first and serve as the evaluation instrument for everything else.
- Pass 1 was right that downstream scores alone cannot answer whether useful latent structure is present.

Grounding:

- Lu-style results suggest weak latent step structure.
- Du/LTO-style results suggest latent correctness signal exists.
- This tension has not been cleanly tested on natural-language multi-hop.

### Exact Method

Question:

`Does base recurrent depth already carry detectable natural-language multi-hop signal?`

Run:

- extract hidden states at recurrence depths `R in {4, 8, 16}`
- use `300` HotpotQA-style 2-hop examples with bridge signal where possible
- use `300` MuSiQue examples if available
- train a simple linear probe on the chosen hidden-state representation
- report AUC by depth

### Primary Metric

- probe AUC by depth

### Win Condition

- materially positive AUC increase with depth, such as delta `>= 0.10`

### Interpretation

- rising AUC: latent multi-hop structure exists and can potentially be amplified
- flat AUC: recurrence is mostly iterative refinement without useful NL multi-hop separation
- declining AUC: overthinking dominates

### Budget

- about `6 GPU-hours`

## Strategy 2: Hop-Aligned Auxiliary Supervision

### Why This Survived

Best combined logic from the two passes:

- Pass 1 correctly identified DACR step structure as a natural latent supervision scaffold.
- Pass 2 correctly converted that into the strongest concrete first-wave method.

Grounding:

- `SIM-CoT` is the strongest current evidence that step-level supervision stabilizes implicit/latent reasoning.
- prior BOTCOIN findings already showed the collapse mode this strategy is meant to prevent

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

Mechanism:

- attach an auxiliary decoder during training only
- supervise intermediate recurrent states against aligned DACR reasoning steps
- remove auxiliary head for inference

### Primary Metrics

- bridge/entity probe improvement over Strategy 1 baseline
- auxiliary step prediction quality

### Behavioral Corroboration

- HotpotQA and DROP movement without collapse

### Win Condition

- meaningful probe improvement over Strategy 1 baseline
- plus evidence that step alignment is non-trivial
- ideally with some behavioral corroboration

### Interpretation

- positive: BOTCOIN traces are useful as latent step teachers
- probe-only movement: structure shift without confirmed downstream benefit yet
- no movement: SIM-CoT-like transfer did not materialize at this scale

### Budget

- about `22 GPU-hours`

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
- dynamic recurrence schedule
- curriculum bucketed by hop count
- measure across multiple inference depths after training

Data:

- DACR bucketed by hop complexity

Eval:

- run benchmark sweeps across `R in {4, 8, 16, 32}` where feasible

### Primary Metric

- behavioral score by inference depth

### Win Condition

- monotone or clearly favorable score scaling from lower to moderate recurrence depth

### Interpretation

- positive: recurrence-aware training transfers to natural-language multi-hop
- flat: recurrence-aware mechanism did not transfer
- decline: overthinking still dominates

### Budget

- about `18 GPU-hours`

## Strategy 4: Trajectory-Classifier Amplification

### Why This Survived

Best combined logic from the two passes:

- Pass 2 correctly preserved this as the main alternative to “install step structure.”
- Pass 1’s emphasis on latent geometry naturally supports a trajectory-level discrimination test.

Grounding:

- `LTO` shows latent correctness signal may already exist
- BOTCOIN raw attempts provide unusually good positive/negative same-task contrasts

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
- reranked HotpotQA-style behavior

### Win Condition

- classifier remains discriminative
- guided selection or reranking yields meaningful lift

### Interpretation

- positive: base latent signal existed and BOTCOIN training sharpened it
- AUC collapse: classifier got gamed
- stable AUC with no behavioral lift: signal did not amplify usefully

### Budget

- about `20 GPU-hours`

## Strategy 5: Boundary-Token Format A/B

### Why This Survived

Best combined logic from the two passes:

- Pass 1 was right that explicit step boundaries may help latent alignment.
- Pass 2 was right that this should be a controlled A/B, not a default assumption.

Grounding:

- step alignment logic from `SIM-CoT`
- prior BOTCOIN collapse on structural-token patterns makes format changes high-risk and high-value

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

### Primary Metrics

- HotpotQA EM delta
- DROP EM delta

### Secondary Metric

- probe AUC delta

### Win Condition

- treatment arm materially beats control, or shows a clear latent-structure win without behavioral loss

### Interpretation

- positive: future BOTCOIN data generation should include boundaries
- near-zero delta: current format is sufficient at this scale
- negative delta: boundaries likely increase harmful format overfitting

### Budget

- about `16 GPU-hours`

## Shared Evaluation Rules Across All Strategies

Every valid strategy result should include:

- post-train output gate result
- benchmark outputs with parseable rate
- probe outputs where applicable
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
- behavior moves
- depth behavior improves
- no collapse

### Weak Positive

- probe moves without clear behavior, or vice versa

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
- if Strategy 5 wins: change BOTCOIN data generation format before larger training
- if Strategy 1 shows no useful structure and the others fail: stop and revisit data/measurement before larger compute

## One-Sentence Mental Model

The first wave is:

`a tightly gated, evidence-ranked probe campaign using the strongest operational parts of Pass 2, sharpened by the best architectural insights from Pass 1, to decide which training method is worth scaling next.`

