# Research Synthesis

This document explains **why the first-wave probe strategies exist**, how the two earlier research passes were weighed against each other, and how those ideas were corrected using the distilled prior experiment findings in this repository plus the strongest current 2025-2026 literature.

The orchestrator should read this before interpreting the strategy matrix. The goal is to prevent cargo-cult execution.

For the included prior-experiment evidence, see `docs/PRIOR_EXPERIMENT_FINDINGS.md`.

## Executive Synthesis

The two research passes contributed different strengths:

- **Pass 1** was strongest on architectural imagination. It surfaced the right high-level intervention families: latent supervision, stability constraints, elastic-depth training, and latent-alignment structure.
- **Pass 2** was stronger operationally. It turned those ideas into budgeted hypotheses, explicit thresholds, GPU-hour estimates, and decision-useful first-wave probes.

The final strategy framing in this repository gives **more operational weight to Pass 2**, but keeps a few of Pass 1's best insights where they sharpen the orchestrator's understanding:

1. looped models fail in **specific**, repeated ways: collapse, rank instability, depth overthinking, and format leakage
2. structured trace data is valuable because it gives **structured multi-hop chains**, but the signal only matters if it transfers to natural-language multi-hop and then to causal reasoning
3. first-wave runs should search for **signal**, not pretend to settle the whole latent-reasoning question

The cleanest summary is:

- **Pass 2 provides the structure**
- **Pass 1 provides the research-backed specificity when an exact design choice determines whether the test is valid**

The transfer rule for this repository is simple:

1. prove scenario structural fidelity first
2. test whether that structure transfers to real natural-language multi-hop
3. only then treat causal reasoning as a meaningful out-of-domain check

## What Was Kept From Each Pass

### From Pass 1

Keep these ideas:

- natural-language multi-hop is harder than synthetic symbol transfer because of aliasing, distractors, unstable semantics, and format artifacts
- step structure in DACR traces can be repurposed into latent supervision
- stability and overthinking are architectural issues, not just optimizer noise
- boundary markers are worth testing as a **data-format A/B**, not assumed improvements

Do **not** inherit Pass 1 literally where it overreaches:

- from-scratch Parcae-scale rebuilding of a new looped model is **not** first-wave priority on an `8xH100` signal-hunt budget
- aggressive architectural rewrites are a second-wave response if first-wave retrofits show real signal
- several ideas in Pass 1 are best treated as conceptual imports, not immediate implementation commitments

### From Pass 2

Keep these ideas:

- probe baseline first
- use pre-registered thresholds
- gate on parseability and prompt contract before training
- treat narrow or format-sensitive benchmarks as secondary early on
- compare strategy mechanisms, not just final scores

Pass 2 is the main operational backbone because it reflects the current recurrent-depth reality:

- previous runs already showed collapse with overly expressive LoRA and too much training
- standard benchmarks exposed transfer better than strict DACR formatting
- the repaired stack corrected stale measurement errors

## What The Existing Experiment Changed

The prior experiment materially changed the framing. These are not optional details.

### 1. The experiment already disproved several naive assumptions

Observed local failures included:

- rank-64 LoRA with small data collapsed into delimiter garbage
- long training with low loss was not “better,” it was memorization
- full-LoRA sometimes looked healthy by loss and still failed output gates
- invalid probe construction and stale measurement paths created misleading confidence

Therefore the orchestrator must assume:

- low loss can be bad
- output gates matter as much as train loss
- probe validity is fragile
- prompt contracts can change the interpretation of the whole run

### 2. The best local positive signal was small, careful, and fragile

The strongest previously repaired positive signal was a **minimal core-only LoRA regime**:

- low rank
- high-loss regime
- short token budget
- core-focused adaptation

That matters because it argues against “just train longer” and supports the idea that first-wave strategies should be:

- conservative
- tightly budgeted
- easy to invalidate

### 3. The training corpus and the probe corpus are not the same object

This was one of the most important local corrections.

- clean-positive training examples are useful for teaching
- balanced positive/negative examples are necessary for probes
- challenge-disjoint or grouped splits are required where possible

Any orchestrator that collapses these into one undifferentiated dataset will likely recreate the previous mistakes.

## Paper-Level Evidence That Actually Matters

The first wave is grounded in a specific evidence stack, not generic “looped transformers are exciting” energy.

### Core architectural papers

#### `Geiping et al. 2025` - `Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach`

Why it matters:

- establishes recurrent depth as a serious test-time compute axis
- legitimizes variable recurrence as a real lever
- supports using a recurrent-depth base model rather than inventing a new architecture first

Operational takeaway:

- use a recurrent-depth base model as the scaffold
- evaluate depth scaling explicitly

#### `Kohli et al. 2026` - `Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers`

Why it matters:

- strongest synthetic evidence for dynamic recurrence, curriculum, and depth extrapolation
- directly studies the gap between train-time reasoning depth and test-time depth
- explicitly documents overthinking

Operational takeaway:

- dynamic `R` and hop-count curriculum deserve a first-wave slot
- overthinking must be measured, not hand-waved

#### `SIM-CoT 2025` - `SIM-CoT: Supervised Implicit Chain-of-Thought`

Why it matters:

- strongest evidence that step-level supervision stabilizes implicit/latent reasoning
- directly addresses the failure mode already observed locally: latent collapse under scaling
- auxiliary decoder is training-only, so it matches a low-regret first-wave intervention

Operational takeaway:

- hop-aligned auxiliary supervision is the **highest-evidence installed-structure strategy**

#### `Encode, Think, Decode 2025` - `Encode, Think, Decode: Scaling test-time reasoning with recursive latent thoughts`

Why it matters:

- shows that recursive latent trajectories can be amplified without changing the base architecture
- creates a credible alternative hypothesis to “install structure from scratch”
- suggests trajectory-level credit assignment may amplify an already present latent signal

Operational takeaway:

- include one strategy that tests **amplification of existing structure**, not only structure installation

#### `LoopFormer 2026`

Why it matters:

- strongest evidence for elastic-depth training and shortcut consistency
- directly addresses the reality that fixed-depth training can make looped models brittle at other depths

Operational takeaway:

- its logic should shape first-wave interpretation and second-wave design
- but full LoopFormer-style architecture changes are better treated as **design priors** and a second-wave scaling path, not the very first `8xH100` run

#### `Parcae 2026`

Why it matters:

- strongest stability paper for from-scratch looped models
- explicitly ties stability to spectral properties and gives scaling-law guidance

Operational takeaway:

- use Parcae to justify second-wave from-scratch work only if first-wave retrofits show signal
- keep Parcae in the synthesis so the orchestrator understands what “next” looks like if retrofits succeed

#### `Yu et al. 2025` - `Causal Sufficiency and Necessity Improves Chain-of-Thought Reasoning`

Why it matters:

- gives the first wave a causal lens for checking whether apparent reasoning gains are actually necessary and sufficient
- is the most direct bridge from multi-hop transfer to causal reasoning transfer
- helps distinguish real reasoning from shortcut learning in the final evaluation ladder

Operational takeaway:

- use a causal suite as the final transfer rung when the environment supports it
- treat a multi-hop-only win as incomplete if the causal rung stays flat

## Why The Five First-Wave Strategies Survived The Weighing Process

The strategies below are not equal-weight copies of the rough passes. They are the result of weighing:

- Pass 1 conceptual ideas
- Pass 2 operational thresholds
- repaired local experiment findings
- late-2025/2026 primary papers

They are also ordered by the transfer ladder that matters for this project:

1. does the model expose scenario structural fidelity at all
2. does that structure transfer to real natural-language multi-hop
3. does it continue to matter on causal reasoning tasks

### Strategy 1: Natural-language latent probe baseline

Why it survived:

- both passes implied that downstream scores alone would not answer the real question
- local experiment history showed measurement bugs can completely distort conclusions
- `Lu-style weak step structure` vs `Du-style strong trajectory signal` is an unresolved tension

Why it is first:

- it determines whether later strategies are trying to **amplify existing structure** or **install missing structure**

Why it is evidence-grounded:

- Pass 2 correctly turned this into the evaluation instrument for everything else
- local repaired findings emphasized that the probe path must be valid before training claims are worth anything

### Strategy 2: Hop-aligned auxiliary supervision

Why it survived:

- this is the cleanest intersection of structured-trace data and current research
- DACR traces already contain explicit step structure
- `SIM-CoT` provides the strongest current mechanism for stabilizing implicit reasoning with step-level targets

Why it is high priority:

- it directly attacks the exact collapse mode already seen in local runs
- it is training-only overhead, not a large architecture rewrite

Why this is grounded in both passes:

- Pass 1 correctly identified latent step alignment as important
- Pass 2 converted that into a concrete, budgeted auxiliary-decoder plan
- repaired findings justified keeping rank and token budget conservative

### Strategy 3: Dynamic recurrence plus hop curriculum

Why it survived:

- `Kohli 2026` is the most principled recipe for recurrence-aware training
- it provides a falsifiable prediction on depth scaling in natural-language multi-hop
- it does not require auxiliary decoders or new model classes

Why it matters:

- it is the best direct test of whether synthetic recurrent-depth results transfer into natural-language multi-hop

Why this is grounded:

- Pass 2 framed this correctly as a clean adjudication between “depth helps if trained right” and “depth yields marginal gains or overthinking”
- local evidence already showed the need to inspect score vs depth rather than score at one fixed depth

### Strategy 4: Trajectory-classifier amplification

Why it survived:

- trajectory-level latent credit assignment work shows the latent signal may already exist
- this gives a mechanistically different bet from Strategies 2 and 3
- DACR has same-task positive/negative attempt structure, which makes it unusually suitable for classifier-driven trajectory supervision

Why it stays in first wave:

- it is comparatively cheap
- it can produce an informative negative if the classifier gets gamed

Why this is grounded:

- Pass 2 correctly recognized this as the main alternative to “install step structure”
- the repaired dataset audit makes clear that raw attempts contain exactly the positive/negative contrasts needed for a real test

### Strategy 5: Boundary-token format A/B

Why it survived:

- Pass 1 was right that explicit boundary structure might help latent alignment
- Pass 2 was right that this should be tested as a **data-format decision**, not assumed
- local failures showed the model can collapse into structural-token garbage, so formatting has to be handled with suspicion

Why it stays in first wave:

- it is a cheap decision with large downstream implications for future data generation

Why this is grounded:

- it is supported by the step-alignment story from `SIM-CoT`
- it is constrained by the local evidence that format-heavy training can fail badly

## What Was Deliberately Demoted

These ideas are not rejected forever. They are demoted because they are not the best first-wave use of an `8xH100` signal-hunt budget.

### Full from-scratch Parcae build

Demoted because:

- highest implementation burden
- strongest benefit appears after first-wave viability is already established
- less aligned with the repaired local recurrent-depth infrastructure

### Large-scale full-parameter continued pretraining

Demoted because:

- too expensive for the first-wave question
- harder to interpret if it works
- too many moving parts for the current measurement maturity

### Pure RL / latent-space RL as the first move

Demoted because:

- current evidence remains weaker than supervised latent alignment and curriculum methods
- adjacent late-2025 evidence suggests latent RL is not yet the best early bet for reliable transfer

## Ranking Logic For The Orchestrator

The orchestrator should hold the following mental model:

1. **Probe baseline first** to determine whether there is latent multi-hop structure worth amplifying.
2. **Try structure-installing strategies with strongest current evidence**:
   - hop-aligned auxiliary supervision
   - dynamic recurrence plus curriculum
3. **Try one structure-amplification strategy**:
   - trajectory classifier
4. **Run the cheap data-format decision in parallel where possible**:
   - boundary-token A/B
5. Use the outcomes to decide whether second wave should be:
   - larger recurrent-depth retrofit,
   - elastic-depth training,
   - or from-scratch stable looped modeling

## What The Orchestrator Must Never Forget

The first wave is not proving “latent reasoning works.”

It is proving, or disproving, a narrower and more decision-useful claim:

`Structured multi-hop traces can measurably shift recurrent hidden-state geometry and then transfer that signal to real natural-language multi-hop reasoning, and ideally to causal reasoning, under a tightly constrained compute budget.`

That framing is the reason the strategy matrix exists in its current form.
