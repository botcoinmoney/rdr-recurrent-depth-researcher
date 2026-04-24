# Next Actions

- Add or remove sources in `manual_data_sources.yaml`.
- If you already have task-specific data, place it in `datasets/`.
- Set `execution.base_model_preset`, `execution.commands.train`, and `execution.commands.eval` in `pipeline.yaml`.
- If the shipped presets do not fit, set `execution.base_model` to override them.
- If you want API-backed ideation, set `idea_generation.llm.provider` in `pipeline.yaml` and export the matching API key.
- If you prefer IDE agents, keep provider=`none` and use `agent_bootstrap.md`.
- Edit `data_recipes.yaml` whenever you want to change the structure, style, or evidence surface of ingested data.
