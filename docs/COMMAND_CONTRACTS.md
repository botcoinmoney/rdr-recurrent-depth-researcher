# Command Contracts

The built-in research pipeline expects your external commands to write JSON to the provided `metrics_path`.

## Train Command

Inputs usually include:

- `base_model`
- `dataset_path`
- `output_dir`
- `knobs`
- `metrics_path`

Recommended outputs:

- `loss`
- `tokens_seen`
- `wallclock_seconds`

## Eval Command

Inputs usually include:

- `model_path`
- `dataset_path`
- `depth`
- `condition`
- `metrics_path`

Recommended outputs:

- `composite_score`
- `accuracy`
- `em`
- `f1`

The harness uses the first available of `composite_score`, `accuracy`, `em`, `f1`, or `score`.

## Probe Command

Inputs usually include:

- `model_path`
- `dataset_path`
- `metrics_path`

Recommended outputs:

- `probe_auc`
- `probe_f1`

## Why This Contract Exists

The harness is trying to stay general across many recurrent-depth stacks while still being fully runnable. Standardizing on JSON outputs is the smallest practical interface that lets the orchestrator remain generic.
