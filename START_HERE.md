# Start Here

The intended workflow is:

1. initialize a workspace
2. point the workspace at a preset base model and real data
3. wire in real train/eval/probe commands
4. let the loop run with Codex, Claude Code, or API mode

## Minimal Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 scripts/setup_env.py --profile auto
rdh init-workspace --workspace /root/rdh-workspace
cd /root/rdh-workspace
```

## Required Edits

Edit `pipeline.yaml`:

- choose `idea_generation.llm.provider`
- choose `execution.base_model_preset`
- optionally override with `execution.base_model`
- set `execution.commands.train`
- set `execution.commands.eval`
- optionally set `execution.commands.probe`

Preset checkpoints shipped by default:

- `huginn_0125` -> `tomg-group-umd/huginn-0125`
- `ouro_1_4b_thinking` -> `ByteDance/Ouro-1.4B-Thinking`
- `ouro_2_6b_thinking` -> `ByteDance/Ouro-2.6B-Thinking`

Edit data inputs:

- place local datasets under `datasets/`, or
- point `manual_data_sources.yaml` at them

Edit transform surface:

- change `data_recipes.yaml` when you want to alter supervision format, style, evidence structure, or control variants

## Run

One cycle:

```bash
rdh run-cycle --workspace .
```

Continuous:

```bash
rdh loop --workspace .
```

## If You Are Using Codex Or Claude Code

Keep `provider: none`, then paste `agent_bootstrap.md` into your IDE agent once.

## If You Are Using APIs

Export the right key, set the provider in `pipeline.yaml`, and run the loop.

## Before You Start Large Runs

Read:

1. [README.md](/root/recurrent-depth-autoresearch-harness/README.md)
2. [docs/GENERALIZED_RECURRENT_DEPTH_LESSONS.md](/root/recurrent-depth-autoresearch-harness/docs/GENERALIZED_RECURRENT_DEPTH_LESSONS.md)
3. [docs/OPENMYTHOS_DEEP_DIVE.md](/root/recurrent-depth-autoresearch-harness/docs/OPENMYTHOS_DEEP_DIVE.md)

The harness is opinionated about controls on purpose. It is trying to reduce false-positive recurrent-depth stories, not just produce more runs.
