# Dependencies And Sources

This document exists so the orchestrator can work from a fresh GPU template without access to the original BOTCOIN system.

Everything needed to understand the run is either:

- included in this repository, or
- listed here as an external dependency with its purpose

## Included In This Repository

These are self-contained in the handoff repo:

- experiment framing
- prior experiment findings
- strategy rationale
- setup instructions
- measurement and gate rules
- run-repo templates
- bootstrap and validation scripts

## External Dependencies

These are not bundled because they are large, authoritative, or need to stay source-of-truth from upstream.

### 1. Base model

- `tomg-group-umd/huginn-0125`

Purpose:

- recurrent-depth base model for the first-wave probe strategies

### 2. BOTCOIN/DACR training data

- `botcoinmoney/domain-agnostic-causal-reasoning-tuning`

Purpose:

- structured multi-hop training traces
- source for SFT, GRPO, PRM, and DPO-style variants

### 3. DACR benchmark

- `github.com/botcoinmoney/dacr-bench`

Purpose:

- secondary behavior benchmark once prompt/output alignment is validated

### 4. Synthetic-to-real training/eval code

- `github.com/botcoinmoney/synthetic-to-real-reasoning`

Purpose:

- reference implementation path for DACR data usage and evaluation patterns if needed

### 5. Standard benchmark sources

Use your standard internal or public access path for:

- HotpotQA
- DROP
- MuSiQue if available

Purpose:

- primary first-wave external behavior checks

## Paper Sources

These papers are not mirrored here, but their relevant conclusions are already distilled into `docs/RESEARCH_SYNTHESIS.md`.

Key references:

- `Geiping et al. 2025` recurrent depth / latent reasoning
- `Kohli et al. 2026` Loop, Think, & Generalize
- `SIM-CoT 2025 / ICLR 2026`
- `LTO 2025 / ICLR 2026`
- `LoopFormer 2026`
- `Parcae 2026`
- `ETD 2025`

## Fresh-System Rule

If the orchestrator is missing information and cannot access the original BOTCOIN machine, it should rely on:

1. the distilled documents in this handoff repo
2. the external sources listed here

It should **not** assume any hidden local files exist elsewhere.

