# Run Manifest Guide

The live run repo should carry a filled-in run manifest before any serious GPU spend begins.

Use `configs/run_manifest.yaml` as the source template, then copy the values into the live run repo and keep them current as the run evolves.

## What The Manifest Is For

The manifest makes the experiment auditable at a glance. It should answer:

1. what exact recurrent-depth transfer question is being tested
2. which real natural-language multi-hop tasks will validate transfer
3. which causal reasoning tasks will validate transfer beyond multi-hop
4. what datasets, prompts, and snapshots were actually used
5. which GPU slots are reserved for training, output gates, and eval
6. which stop conditions invalidate a variant

## Required Fields

At minimum, record:

- machine inventory
- auth and cache state
- model commit or checkpoint identifier
- dataset snapshot IDs and split rules
- baseline anchor values
- GPU map and eval slack
- per-variant checklist status
- stop conditions
- findings log pointer

## Recommended Transfer Ladder

Keep the manifest aligned to three rungs:

1. `scenario structural fidelity`
2. `real natural-language multi-hop transfer`
3. `causal reasoning transfer`

The run is only interesting if a strategy moves at least one rung upward without breaking the earlier rungs.

## Operational Checklist

Before training:

- record the prompt contract hash
- record the current benchmark anchor
- confirm no stale probe artifacts are being reused
- confirm the output-gate path has reserved capacity
- confirm the transfer ladder targets are written down

After each checkpoint:

- run the output gate immediately
- mark the variant invalid if parseability fails
- record probe and benchmark outcomes in the manifest or findings log
- note whether the result helps multi-hop transfer, causal transfer, both, or neither

At closeout:

- record the best supported rung reached by each strategy
- record whether the result is a structure-install win, structure-amplification win, or a transfer failure
- record the next most defensible experiment
