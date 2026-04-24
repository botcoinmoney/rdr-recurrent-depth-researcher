# Runtime Setup

Use the environment bootstrap instead of manually juggling environment-specific installs.

## Profiles

- `auto`
- `cpu_local`
- `single_gpu`
- `multi_gpu`
- `cluster_shared`
- `h100_4gpu`
- `h100_8gpu`

## Recommended

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 scripts/setup_env.py --profile auto
```

## Explicit

```bash
python3 scripts/setup_env.py --profile single_gpu
python3 scripts/setup_env.py --profile multi_gpu
python3 scripts/setup_env.py --profile cluster_shared
```

## What It Pins

- base runtime deps
- optional dev/test deps
- PyTorch wheel line per environment profile
- virtualenv target path
- recommended cache exports

## Why This Exists

The repo needs a lightweight setup path that still behaves predictably across machines. The environment profiles and install matrix keep the surface area small while avoiding one-size-fits-all PyTorch pinning in `pyproject.toml`.

## Full Structural Simulation

If you want to verify the end-to-end orchestration flow locally before using real hardware:

```bash
bash scripts/simulate_full_loop.sh
```

That simulation exercises handoff creation, workspace setup, repeated cycles, report generation, and automatic git progression.
