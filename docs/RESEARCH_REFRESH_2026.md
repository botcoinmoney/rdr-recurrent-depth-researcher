# Research Refresh: April 22, 2026

This document refreshes the handoff package against the most relevant recurrent-depth, latent-reasoning, and reasoning-transfer papers available as of **April 22, 2026**.

Use it to keep wave-1 decisions grounded in current evidence rather than in a frozen 2025 picture.

## Why This Refresh Exists

The earlier repository framing was already directionally strong, but the current literature sharpens three practical points:

1. recurrent depth is now a real compute axis, not just a speculative architectural trick
2. latent reasoning exists in useful forms, but it is unstable, depth-sensitive, and only partially readable
3. success on symbolic or synthetic hop structure does **not** automatically transfer to real natural-language multi-hop or causal reasoning

That third point matters most for any scenario built from structured traces or synthetic reasoning artifacts.

Structured challenge traces are valuable because they expose:

- multi-hop decompositions
- same-task positive and negative attempts
- causal chains and counterfactual mistakes

But they only become useful for **real language** if training and evaluation explicitly force transfer across:

- paraphrase variation
- entity aliasing
- distractor evidence
- retrieval ambiguity
- causal directionality

## Primary-Source Shortlist

### Recurrent Depth And Latent Compute

#### `Geiping et al., 2025`
`Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach`
arXiv: `2502.05171`, posted `February 7, 2025`

Why it matters:

- strongest direct case for latent test-time compute via recurrent depth
- supports using a recurrent-depth base model for wave 1 rather than starting with a large rebuild

#### `Lu et al., 2025`
`Latent Chain-of-Thought? Decoding the Depth-Recurrent Transformer`
arXiv: `2507.02199`, posted `July 2, 2025`

Why it matters:

- shows that latent reasoning can be weakly readable and lens-sensitive
- supports running more than one probe family and not overclaiming from a single interpretability view

#### `Wei et al., 2025`
`SIM-CoT: Supervised Implicit Chain-of-Thought`
arXiv: `2509.20317`, posted `September 24, 2025`

Why it matters:

- strongest current step-aligned supervision result for stabilizing latent reasoning
- directly matches the opportunity to convert explicit traces into stable latent states

#### `Koishekenov et al., 2025`
`Encode, Think, Decode: Scaling test-time reasoning with recursive latent thoughts`
arXiv: `2510.07358`, posted `October 8, 2025`

Why it matters:

- strongest retrofit path for iterating only a subset of reasoning-heavy layers
- useful if full recurrent-depth fine-tuning is too expensive or too invasive

#### `Jeddi et al., 2026`
`LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation`
arXiv: `2602.11451`, posted `February 11, 2026`

Why it matters:

- strongest current elastic-depth training recipe
- supports evaluating whether strategy families scale smoothly across different recurrence budgets

#### `Kohli et al., 2026`
`Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers`
arXiv: `2604.07822`, posted `April 9, 2026`

Why it matters:

- best current evidence for depth extrapolation, curriculum, and overthinking analysis
- directly supports the dynamic-recurrence-plus-curriculum slot in the strategy matrix

#### `Prairie et al., 2026`
`Parcae: Scaling Laws For Stable Looped Language Models`
arXiv: `2604.12946`, posted `April 14, 2026`

Why it matters:

- strongest current stability framing for looped language models
- pushes second-wave thinking toward spectral stability and loop/data co-scaling

### Hybrid Latent/Text Reasoning

#### `ThinkRouter, 2026`
`ThinkRouter: Efficient Reasoning via Routing Thinking between Latent and Discrete Spaces`
arXiv: `2602.11683`, posted `February 2026`

Why it matters:

- strongest current case for not forcing every example into purely latent or purely textual reasoning
- makes a gated hybrid fallback more defensible if pure latent transfer underperforms on real language

### Transfer Into Real Multi-Hop And Causal Reasoning

#### `Back Attention, 2025`
`Back Attention: Understanding and Enhancing Multi-Hop Reasoning in Large Language Models`
arXiv: `2502.10835`, posted `February 2025`

Why it matters:

- useful mechanistic framing for where multi-hop composition fails
- supports measuring evidence routing, not just final answer accuracy

#### `ReasonBridge, 2025`
`ReasonBridge: Efficient Reasoning Transfer from Closed to Open-Source Language Models`
arXiv: `2506.22865`, posted `June 2025`

Why it matters:

- strong teacher-transfer framing for reasoning trajectories
- suggests structured traces should be paired with natural-language paraphrase targets when possible

#### `Causal Distillation, 2025`
`Causal Distillation: Transferring Structured Explanations from Large to Compact Language Models`
arXiv: `2505.19511`, posted `May 2025`

Why it matters:

- best direct support for preserving causal directionality during transfer
- helps distinguish genuine causal transfer from shallow step imitation

## Updated Position

The strongest April 2026 framing is:

- use structured challenge data to teach **latent transition structure**
- use real natural-language benchmarks to test whether that structure survives paraphrase, aliasing, distractors, and evidence selection
- treat causal reasoning as a separate transfer target, not as a deeper version of plain multi-hop

In practice, the wave-1 plan should track four layers of success:

1. symbolic hop structure
2. latent trajectory geometry
3. natural-language evidence routing
4. causal direction and counterfactual robustness

If a strategy improves only layer 1, it is not yet a real transfer win.

## Concrete Implications For Wave 1

### 1. Probe baselines must include real language stressors

Do not rely on only one balanced probe corpus.

Probe sets should cover:

- bridge-style natural-language QA
- causal QA or causal plausibility checks
- paraphrase and alias stress tests

### 2. Auxiliary supervision should target hop roles, not just hop order

Prefer role labels like:

- retrieve support
- resolve alias
- bridge entity
- reject distractor
- infer causal link

That is more useful than only teaching step positions `1`, `2`, `3`, and `4`.

### 3. Curriculum should increase language entropy, not only hop depth

A better curriculum axis is:

- synthetic clean chains
- templated natural language
- paraphrased natural language
- distractor-heavy multi-document natural language

### 4. Trajectory scoring should include causal usefulness

Positive and negative attempts should be labeled for:

- final correctness
- evidence sufficiency
- distractor susceptibility
- causal direction correctness

### 5. Hybrid fallback is now evidence-backed

If pure latent transfer shows promising probes but weak real-language behavior, the next move does not need to be “abandon latent reasoning.”

A defensible fallback is:

- latent recurrence for cheap internal refinement
- explicit natural-language scratchpad only on uncertain or causal-heavy cases

## Recommended Read Order

1. `Geiping et al. 2025`
2. `Lu et al. 2025`
3. `SIM-CoT 2025`
4. `LoopFormer 2026`
5. `Kohli et al. 2026`
6. `Parcae 2026`
7. `ThinkRouter 2026`
8. `ReasonBridge 2025`
9. `Causal Distillation 2025`

## Bottom Line

The most defensible first move is still a tightly gated **signal hunt**.

As of `April 22, 2026`, that signal hunt should be judged by whether structured supervision transfers into:

- real natural-language multi-hop reasoning
- causal directionality
- robustness to paraphrase and distractors
- useful depth scaling without overthinking
