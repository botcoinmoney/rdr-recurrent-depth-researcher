# E2E Simulation

Run this when you want a full local sanity check of the orchestration path without needing a real GPU cluster.

It simulates:

- root repo preflight
- live run repo creation
- handoff preflight inside that live repo
- standalone workspace initialization
- local dataset materialization
- train/eval/probe command execution
- repeated loop cycles
- findings, handoff, reports, and git commits

Command:

```bash
bash scripts/simulate_full_loop.sh
```

The simulation uses:

- a temporary local-only live run repo
- a temporary standalone workspace
- tiny local train/eval/probe scripts
- CPU-only execution with fake metrics shaped like a real control-aware loop

This is a structural sanity check, not a model-quality benchmark. Its purpose is to prove that the orchestration path has no missing steps, dead ends, or human-required glue in the normal loop lifecycle.
