# Agent Bootstrap

Prompt for Codex or Claude Code:

```text
Read pipeline.yaml, data_recipes.yaml, findings.md, HANDOFF.md, and the latest file under reports/.
Then continue the recurrent-depth loop with minimal human intervention.
You should:
- refresh research and data catalogs when stale
- validate that baseline, candidate, and scramble-control comparisons remain intact before launching work
- preserve the required controls in pipeline.yaml
- adjust data format through data_recipes.yaml or local dataset transforms when that is the highest-leverage path
- run benchmark and probe paths that can actually falsify the current hypothesis, not only the easiest path to produce a positive-looking result
- keep findings.md and HANDOFF.md current
- commit at the end of meaningful progress checkpoints
- leave the workspace in a resumable state after each cycle
Avoid optimizing for format imitation alone; prioritize real latent-transfer signal, absolute deep-depth behavior, and clean control comparisons.
```
