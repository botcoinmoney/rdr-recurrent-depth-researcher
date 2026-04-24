# Workspace

This directory is the standalone execution surface for the recurrent-depth harness.

Recommended loop:

1. Add manual datasets or repos to `manual_data_sources.yaml`.
2. Optionally copy local corpora into `datasets/`.
3. Edit `pipeline.yaml` so `execution.base_model_preset`, `execution.commands.train`, and `execution.commands.eval` point at your real stack.
4. Edit `data_recipes.yaml` if you want different supervision or control formats.
5. Run `rdh refresh-research --workspace .`
6. Run `rdh discover-data --workspace .`
7. Run `rdh run-cycle --workspace .` or `rdh loop --workspace .`
8. If you are using Codex or Claude Code, load `agent_bootstrap.md` into the session.
9. Review `findings.md`, `HANDOFF.md`, and the latest `reports/cycle-*.md` after each cycle.

The harness keeps snapshots in:

- `research/latest_research.json`
- `datasets/catalog.json`
- `reports/`
- `runs/`
- `data_recipes.yaml`
- `agent_bootstrap.md`

It also updates:

- `findings.md`
- `HANDOFF.md`
- git history, if the workspace is or becomes a git repo

Default base model presets:

- `huginn_0125` -> `tomg-group-umd/huginn-0125`
- `ouro_1_4b_thinking` -> `ByteDance/Ouro-1.4B-Thinking`
- `ouro_2_6b_thinking` -> `ByteDance/Ouro-2.6B-Thinking`

If you need a different checkpoint, set `execution.base_model` and it will override the preset.
