# Recurrent-Depth Autoresearch Harness

This repo is a standalone harness for running **continuous recurrent-depth research loops** with as little human involvement as possible after setup.

It began as internal infrastructure for experimenting with how BOTCOIN-style structured reasoning data could be optimized for recurrent-depth training and evaluation. That narrower workflow was generalized into a standalone tool for exploring recurrent-depth improvement on any scenario with editable data format, training recipes, controls, benchmarks, and loop logic.

It is built for three modes:

- `Codex` or `Claude Code` in your IDE
- `OpenAI API`
- `Anthropic API`

The harness handles the recurring work:

- refresh research
- discover datasets/repos
- materialize data-format variants
- run baseline vs candidate vs scramble-control experiments
- sweep recurrence depth
- log findings
- refresh `HANDOFF.md`
- commit progress automatically

The human should mostly do setup, occasional heartbeat checks, and strategic intervention when a new direction is clearly warranted.

## Full Simulation

To sanity-check the whole orchestration path locally before running on real hardware:

```bash
bash scripts/simulate_full_loop.sh
```

That script creates a temporary local-only live run repo, initializes a standalone workspace, injects tiny train/eval/probe scripts, runs repeated cycles, and verifies that findings, handoff, reports, and git commits all advance without human intervention.

## Fastest Start

```bash
git clone https://github.com/botcoinmoney/recurrent-depth-autoresearch-harness.git
cd recurrent-depth-autoresearch-harness
python3 -m venv .venv
. .venv/bin/activate
python3 scripts/setup_env.py --profile auto
rdh init-workspace --workspace ./rdh-workspace
cd ./rdh-workspace
```

To force a profile instead of auto-detecting:

```bash
make setup-single
make setup-multi
make setup-cluster
```

Then make only these edits:

1. Put the working dataset in `datasets/` or point `manual_data_sources.yaml` at it.
2. Pick `execution.base_model_preset` in `pipeline.yaml`, or override with `execution.base_model` if a different checkpoint is needed.
3. Set `execution.commands.train` and `execution.commands.eval` in `pipeline.yaml`.
4. Optionally set `execution.commands.probe`.
5. Choose `idea_generation.llm.provider`:
   - `none` for Codex/Claude IDE mode
   - `openai` for API mode
   - `anthropic` for API mode

Then start:

```bash
rdh loop --workspace . --max-cycles 0
```

`0` means unbounded looping.

## Lightweight IDE Mode

To run the loop from Codex or Claude Code in an IDE:

1. Keep `idea_generation.llm.provider: none`
2. Open the workspace
3. Paste the contents of `agent_bootstrap.md` into the IDE agent once
4. Let it run

The harness still handles the file structure, run logging, findings updates, handoff updates, and git commits.

## Lightweight API Mode

OpenAI:

```bash
export OPENAI_API_KEY=...
```

Anthropic:

```bash
export ANTHROPIC_API_KEY=...
```

Then set the provider in `pipeline.yaml` and run:

```bash
rdh loop --workspace .
```

## Runtime Profiles

Setup is profile-driven so different machines do not need different README branches.

Available profiles:

- `auto`
- `single_gpu`
- `multi_gpu`
- `cluster`

Programmatic setup surfaces:

- [scripts/setup_env.py](/root/recurrent-depth-autoresearch-harness/scripts/setup_env.py)
- [src/rdharness/environment.py](/root/recurrent-depth-autoresearch-harness/src/rdharness/environment.py)
- [configs/environment/install_matrix.yaml](/root/recurrent-depth-autoresearch-harness/configs/environment/install_matrix.yaml)
- [configs/environment/single_gpu.yaml](/root/recurrent-depth-autoresearch-harness/configs/environment/single_gpu.yaml)
- [configs/environment/multi_gpu.yaml](/root/recurrent-depth-autoresearch-harness/configs/environment/multi_gpu.yaml)
- [configs/environment/cluster_shared.yaml](/root/recurrent-depth-autoresearch-harness/configs/environment/cluster_shared.yaml)
- [configs/environment/cpu_local.yaml](/root/recurrent-depth-autoresearch-harness/configs/environment/cpu_local.yaml)

Pinned install matrix:

- base packages
- dev packages
- PyTorch wheel line per environment profile
- venv target path
- recommended cache env vars

The intent is simple:

- keep the package metadata lightweight
- pin core versions where environment drift hurts reproducibility
- let PyTorch vary by machine profile instead of pretending one wheel fits every system

## Cluster Launch Readiness

For shared clusters and multi-node jobs, the repo now includes a concrete Slurm launch contract for both `torchrun` and `accelerate`.

Key surfaces:

- [docs/CLUSTER_READINESS.md](/root/recurrent-depth-autoresearch-harness/docs/CLUSTER_READINESS.md)
- [scripts/cluster_contract_check.py](/root/recurrent-depth-autoresearch-harness/scripts/cluster_contract_check.py)
- [templates/slurm/torchrun.sbatch](/root/recurrent-depth-autoresearch-harness/templates/slurm/torchrun.sbatch)
- [templates/slurm/accelerate.sbatch](/root/recurrent-depth-autoresearch-harness/templates/slurm/accelerate.sbatch)

Quick check:

```bash
python3 scripts/cluster_contract_check.py --launcher torchrun
python3 scripts/cluster_contract_check.py --launcher accelerate
```

## How The Stack Works

The built-in execution path is a real multi-stage orchestration layer around the actual model stack:

1. resolve a local dataset source
2. materialize candidate/control/eval dataset variants from `data_recipes.yaml`
3. evaluate the no-adapter baseline depth curve
4. train the candidate variant
5. train the matched scramble control
6. run depth sweeps on each variant
7. optionally run latent probes
8. aggregate control-aware metrics
9. write findings, handoff, reports, and git commits

The only required project-specific integration is the train/eval/probe command layer. The harness handles the recurrent research loop around it.

## The Smallest Working `pipeline.yaml` Edits

```yaml
idea_generation:
  llm:
    provider: openai
    model: gpt-5.4

execution:
  mode: builtin_research_pipeline
  base_model_preset: huginn_0125
  # Optional manual override:
  # base_model: /absolute/path/to/base-model-or-checkpoint
  commands:
    train: >-
      {{python}} /absolute/path/to/train.py
      --base-model {{base_model}}
      --train-data {{dataset_path}}
      --output-dir {{output_dir}}
      --knobs '{{knobs}}'
      --metrics-path {{metrics_path}}
    eval: >-
      {{python}} /absolute/path/to/eval.py
      --model {{model_path}}
      --eval-data {{dataset_path}}
      --depth {{depth}}
      --condition {{condition}}
      --metrics-path {{metrics_path}}
    probe: >-
      {{python}} /absolute/path/to/probe.py
      --model {{model_path}}
      --eval-data {{dataset_path}}
      --metrics-path {{metrics_path}}
```

The external commands should write JSON metrics to `{{metrics_path}}`.

## Base Model Presets

The default pipeline now ships with decided public recurrent-depth presets:

- `huginn_0125` -> `tomg-group-umd/huginn-0125`
- `ouro_1_4b_thinking` -> `ByteDance/Ouro-1.4B-Thinking`
- `ouro_2_6b_thinking` -> `ByteDance/Ouro-2.6B-Thinking`

Set `execution.base_model_preset` to choose one. If a different checkpoint is needed, set `execution.base_model` and it will override the preset.

## Data Format Is First-Class

The harness assumes data structure and style are often the highest-leverage variables in recurrent-depth work.

That is why each workspace includes `data_recipes.yaml`, which controls the dataset variants used by the loop. Out of the box it supports:

- `identity`
- `scramble_preserve_format`
- `evidence_ablate`
- `evidence_slice`
- `minimal_correction`
- `boundary_markers`
- `contrastive_correction`

A variant can be materialized directly for inspection:

```bash
rdh materialize-data \
  --workspace . \
  --source ./datasets/my_data.jsonl \
  --recipe evidence_slice \
  --output ./datasets/preview-evidence-slice.jsonl
```

This is intentional: changing data structure, format, style, and supervision surface should be easy and explicit.

## Research Controls Baked In

The loop is grounded by the prior recurrent-depth findings distilled in this repo:

- no-adapter baseline depth curves are mandatory
- absolute deep-depth performance matters as much as slope
- matched scramble controls are mandatory
- evidence availability is part of the mechanism
- latent and surface metrics must be separated
- one recurrence depth is never enough

It also exposes `OpenMythos`-inspired mechanism families as dynamic knobs instead of assumptions:

- loop-depth scheduling
- depth extrapolation
- evidence reinjection
- stability constraints
- adaptive halting
- loop-index signaling
- per-loop adapters
- recurrent MoE vs dense FFNs
- attention/cache mode
- prelude/recurrent/coda partitioning

See:

- [docs/GENERALIZED_RECURRENT_DEPTH_LESSONS.md](/root/recurrent-depth-autoresearch-harness/docs/GENERALIZED_RECURRENT_DEPTH_LESSONS.md)
- [docs/OPENMYTHOS_DEEP_DIVE.md](/root/recurrent-depth-autoresearch-harness/docs/OPENMYTHOS_DEEP_DIVE.md)
- [docs/COMMAND_CONTRACTS.md](/root/recurrent-depth-autoresearch-harness/docs/COMMAND_CONTRACTS.md)
- [docs/RUNTIME_SETUP.md](/root/recurrent-depth-autoresearch-harness/docs/RUNTIME_SETUP.md)
- [docs/E2E_SIMULATION.md](/root/recurrent-depth-autoresearch-harness/docs/E2E_SIMULATION.md)

## Influences

Several design choices in this harness were shaped by recurrent-depth and latent-reasoning work that kept recurring during the research process:

- `Geiping et al. 2025`, *Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*
- `Kohli et al. 2026`, *Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers*
- `Wei et al. 2025`, *SIM-CoT: Supervised Implicit Chain-of-Thought*
- `Jeddi et al. 2026`, *LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation*
- `Prairie et al. 2026`, *Parcae: Scaling Laws For Stable Looped Language Models*
- `OpenMythos`: https://github.com/kyegomez/OpenMythos

Those influences show up here as concrete harness features rather than as hardcoded beliefs: depth sweeps, scramble controls, evidence ablations, structural data recipes, dynamic recurrent knob families, and control-aware ranking.

## Early Recipe Signals

Some of the strongest setup-level signals from the earlier recurrent-depth experiments were simple recipe choices rather than new architecture:

- **Stop earlier, not later.** For the `S2`-style `alpha=0.05, R_aux=4` recipe, performance was materially better around step `60` than step `120`. Longer training degraded both behavior and coherence.
- **Keep auxiliary depth pressure shallow.** In the `Strategy-2` family, `alpha=0.1, R_aux=4` preserved behavior much better than nearby harsher settings. Higher `R_aux` values increased damage to transfer metrics even when some latent structure looked stronger.
- **Treat `alpha` as a depth-shaping knob.** The latent-signal peak moved with `alpha`: baseline peaked around `R=8`, `alpha=0.1` shifted the peak toward `R=4`, `alpha=0.3` pushed it toward `R=16`, and `alpha=1.0` flattened the curve.

These are not universal laws, but they are good defaults to test early: conservative stopping, modest auxiliary pressure, and explicit measurement of how the latent peak shifts across recurrence depth.

## Workspace Files That Matter

- `pipeline.yaml`: mission, knobs, commands, loop behavior
- `manual_data_sources.yaml`: local or remote sources to surface
- `data_recipes.yaml`: editable data-format and structure transforms
- `agent_bootstrap.md`: one-shot kickoff prompt for Codex/Claude
- `findings.md`: rolling findings log
- `HANDOFF.md`: latest resumable state
- `reports/`: cycle JSON and markdown summaries

## Commands

- `python3 scripts/setup_env.py --profile auto`
- `rdh init-workspace --workspace ./rdh-workspace`
- `rdh validate-config --config ./rdh-workspace/pipeline.yaml`
- `rdh refresh-research --workspace ./rdh-workspace`
- `rdh discover-data --workspace ./rdh-workspace`
- `rdh materialize-data --workspace ./rdh-workspace --source ./datasets/data.jsonl --recipe evidence_slice --output ./datasets/out.jsonl`
- `rdh run-cycle --workspace ./rdh-workspace`
- `rdh loop --workspace ./rdh-workspace`

## Validation

```bash
make validate
make test
```

## Outcome

The intended outcome is a repo that can be cloned or forked, pointed at a base model and local data, given train/eval commands, run in Codex/Claude or API mode, and then left to iterate with minimal ongoing supervision.
