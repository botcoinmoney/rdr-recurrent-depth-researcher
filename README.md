# Recurrent-Depth Autoresearch Harness

This repo is a standalone harness for running **continuous recurrent-depth research loops** with as little human involvement as possible after setup.

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

If you want to force a profile instead of auto-detecting:

```bash
make setup-single
make setup-multi
make setup-cluster
```

Then do only these edits:

1. Put your local dataset in `datasets/` or point `manual_data_sources.yaml` at it.
2. Pick `execution.base_model_preset` in `pipeline.yaml`, or override with `execution.base_model` if you need a different checkpoint.
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

If you want Codex or Claude Code to drive the loop from your IDE:

1. Keep `idea_generation.llm.provider: none`
2. Open the workspace
3. Paste the contents of `agent_bootstrap.md` to your agent once
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

## What Makes This A Real Harness

This is not a toy planner and it no longer ships with a mock runner.

The built-in execution path is a real multi-stage orchestration layer around your actual model stack:

1. resolve a local dataset source
2. materialize candidate/control/eval dataset variants from `data_recipes.yaml`
3. evaluate the no-adapter baseline depth curve
4. train the candidate variant
5. train the matched scramble control
6. run depth sweeps on each variant
7. optionally run latent probes
8. aggregate control-aware metrics
9. write findings, handoff, reports, and git commits

You plug in your actual train/eval/probe commands. The harness plugs them into a repeatable recurrent-depth research loop.

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

Your commands should write JSON metrics to `{{metrics_path}}`.

## Base Model Presets

The default pipeline now ships with decided public recurrent-depth presets:

- `huginn_0125` -> `tomg-group-umd/huginn-0125`
- `ouro_1_4b_thinking` -> `ByteDance/Ouro-1.4B-Thinking`
- `ouro_2_6b_thinking` -> `ByteDance/Ouro-2.6B-Thinking`

Set `execution.base_model_preset` to choose one. If you need something else, set `execution.base_model` and it will override the preset.

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

You can materialize a variant directly to inspect it:

```bash
rdh materialize-data \
  --workspace . \
  --source ./datasets/my_data.jsonl \
  --recipe evidence_slice \
  --output ./datasets/preview-evidence-slice.jsonl
```

This is intentional: changing data structure, format, style, and supervision surface should be easy and explicit.

## Research Controls Baked In

The loop is grounded by the prior findings you provided:

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

## Workspace Files That Matter

- `pipeline.yaml`: mission, knobs, commands, loop behavior
- `manual_data_sources.yaml`: local or remote sources you want surfaced
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

Someone should be able to clone or fork this, point it at a base model and local data, add a train/eval command, choose Codex/Claude or API mode, and then let it keep iterating with minimal ongoing supervision.
