# OpenMythos Deep Dive

This note records what is useful from `kyegomez/OpenMythos` for the harness.

## Important Framing

- `OpenMythos` explicitly presents itself as an independent theoretical reconstruction, not an Anthropic primary source.
- That means it should be used here as a hypothesis generator, not as evidence that Anthropic uses any specific mechanism.

Repository:

- https://github.com/kyegomez/OpenMythos

## Pieces Worth Turning Into Knobs

### 1. Loop-depth scheduling

Useful because recurrent-depth work already depends heavily on evaluating across multiple `R` values.

Harness knob:

- `loop_depth_schedule`
- `depth_extrapolation_probe`

### 2. Frozen input reinjection

OpenMythos repeatedly emphasizes carrying a frozen encoded input through every loop to reduce drift. That is interesting for any setting where evidence, retrieval slices, or task anchors may get washed out across recurrence.

Harness knob:

- `evidence_injection_mode`

### 3. Stability constraints

The LTI-style recurrent update is one of the most concrete ideas in the repo. It does not need to be accepted wholesale to be useful as a test family.

Harness knob:

- `stability_constraint`

### 4. ACT-style halting

Adaptive halting is a plausible compute-allocation mechanism for recurrent blocks. It is worth testing as a variable policy, especially when the harness is comparing easy versus hard examples.

Harness knob:

- `halting_policy`

### 5. Loop-index signaling

Shared recurrent weights may still need a sense of which loop iteration they are in. Loop-index embeddings are a clean way to expose that as an experiment dimension.

Harness knob:

- `loop_index_signal`

### 6. Per-loop adapters

OpenMythos uses loop-specific low-rank modulation. This is worth testing carefully, but your prior findings mean it must be judged against scramble controls and absolute deep-depth performance so it does not get mistaken for shallow format repair.

Harness knob:

- `per_loop_adapter`

### 7. Sparse recurrent FFN structure

The repo places MoE structure specifically in the recurrent block. That is a meaningful architecture hypothesis, but it should stay a toggle, not an assumption.

Harness knob:

- `recurrent_ffn_mode`

### 8. Attention/cache regime

MLA and GQA are mostly systems choices, but they matter when deeper recurrent sweeps become too expensive to run. The harness therefore keeps them as operational knobs rather than latent-reasoning claims.

Harness knob:

- `attention_cache_mode`

### 9. Prelude / recurrent / coda partitioning

The prelude/recurrent/coda split is useful as a generalized design family even if the exact partition is speculative.

Harness knob:

- `scaffold_partition`

## Pieces I Did Not Promote

- direct claims that Anthropic definitely uses this architecture
- strong claims about systematic generalization from the repo alone
- any assumption that MoE, MLA, or ACT are inherently reasoning-improving rather than compute-shaping

## Bottom Line

`OpenMythos` is helpful as a menu of recurrent-depth hypotheses. It is not strong enough to hardcode into the harness as truth. The right use is exactly what the harness now does: expose the plausible mechanisms as reusable knob families and force them through the stronger evaluation controls learned from your prior runs.
