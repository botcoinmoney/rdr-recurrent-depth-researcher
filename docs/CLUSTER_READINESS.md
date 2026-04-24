# Cluster Readiness

This document defines the concrete launch contract for running the harness on shared GPU clusters, especially Slurm-managed multi-node environments.

## Scope

This repo does not replace an actual trainer. It defines the orchestration and launch contract around the trainer so that:

- node startup is deterministic
- `torchrun` or `accelerate` invocation is unambiguous
- checkpoint and restart behavior is explicit
- orchestrator loops do not dead-end on scheduler or rendezvous failures

## Non-Negotiable Launch Rules

1. Use exactly one distributed launcher per job step.
2. Do not nest `accelerate launch` inside `torchrun`, and do not wrap `torchrun` inside an already multi-process trainer.
3. Prefer one Slurm task per node and let the launcher spawn one worker per GPU.
4. Export `SLURM_EXPORT_ENV=ALL` in batch jobs so `srun` steps inherit the intended environment.
5. Use a unique rendezvous id per job or restart lineage.
6. Write checkpoints and logs to durable shared storage, not only to node-local scratch.

## Recommended Slurm Pattern

Recommended model:

- `sbatch` allocates the nodes
- `srun --ntasks=${NNODES} --ntasks-per-node=1` starts one launcher agent per node
- `torchrun` or `accelerate launch` spawns one process per visible GPU on that node

This avoids the common anti-pattern where Slurm spawns one task per GPU and then `torchrun` tries to spawn again.

## Torchrun Contract

Preferred multi-node arguments:

- `--nnodes`
- `--nproc-per-node`
- `--node_rank`
- `--rdzv-id`
- `--rdzv-backend=c10d`
- `--rdzv-endpoint=${MASTER_ADDR}:${MASTER_PORT}`

Recommended operational stance:

- use `c10d` rendezvous unless there is a strong reason to manage `etcd`
- keep `--max-restarts=0` for first-wave experiments unless the trainer is explicitly written for elastic restarts
- treat true elastic membership change as a separate design decision, not a default convenience

Important implication:

- rank identity is not stable across re-rendezvous

That means:

- checkpoint ownership cannot depend on stable global ranks
- sidecar files should key off step or checkpoint ids, not only rank ids
- resume logic should discover the latest durable checkpoint rather than assuming rank-0 wrote the last authoritative state in a stable way

## Accelerate Contract

Use `accelerate launch` only when the trainer already follows the Accelerate execution model.

For multi-node launch, the critical fields are:

- `--num_machines`
- `--num_processes`
- `--machine_rank`
- `--main_process_ip`
- `--main_process_port`

Recommended stance:

- use `static` rendezvous unless elastic recovery is intentionally engineered and tested
- keep the Accelerate config file under version control in the live run repo when it is part of the actual launch surface

## Slurm Environment Contract

The launch layer should capture and log at least:

- `SLURM_JOB_ID`
- `SLURM_JOB_NODELIST`
- `SLURM_JOB_NUM_NODES` or `SLURM_NNODES`
- `SLURM_NODEID`
- `CUDA_VISIBLE_DEVICES`
- `MASTER_ADDR`
- `MASTER_PORT`
- `RDZV_ID`

Recommended derivation:

- `MASTER_ADDR`: first hostname from `scontrol show hostnames "$SLURM_JOB_NODELIST"`
- `MASTER_PORT`: deterministic job-scoped port derived from `SLURM_JOB_ID` unless the cluster requires a fixed port policy
- `RDZV_ID`: `rdh-${SLURM_JOB_ID}` or an explicit restart-lineage id

## Failure Recovery Semantics

### 1. Worker process failure

Symptoms:

- one local rank exits
- the launcher tears down the worker group

Response:

- preserve stderr/stdout for that node
- mark the cycle as failed unless the trainer explicitly supports restart
- resume from the latest durable checkpoint only after the root cause is understood

### 2. Rendezvous failure

Symptoms:

- timeout joining rendezvous
- stale or conflicting rendezvous id
- unreachable master address or blocked port

Response:

- log the exact `MASTER_ADDR`, `MASTER_PORT`, `RDZV_ID`, and node list
- do not blindly rerun with the same rendezvous lineage if stale state is suspected
- create a fresh rendezvous id when restarting from a new Slurm allocation

### 3. Node failure or preemption

Symptoms:

- scheduler kills a node
- all workers terminate due to group failure

Response:

- treat this as a scheduler-level recovery path, not an in-process retry
- rely on durable checkpoints plus batch requeue or a fresh allocation
- ensure the latest completed checkpoint is externally visible before expensive eval fan-out begins

### 4. Slurm requeue

Recommended behavior:

- make the batch script idempotent
- allow re-entry from a known checkpoint path
- record restart lineage in findings or launch logs
- avoid writing ambiguous “latest” artifacts without a monotonic step id

## Ready-to-Use Helpers

Repo surfaces for this:

- [scripts/cluster_contract_check.py](/root/recurrent-depth-autoresearch-harness/scripts/cluster_contract_check.py)
- [templates/slurm/torchrun.sbatch](/root/recurrent-depth-autoresearch-harness/templates/slurm/torchrun.sbatch)
- [templates/slurm/accelerate.sbatch](/root/recurrent-depth-autoresearch-harness/templates/slurm/accelerate.sbatch)

Quick check:

```bash
python3 scripts/cluster_contract_check.py --launcher torchrun
python3 scripts/cluster_contract_check.py --launcher accelerate
```

## References

Primary sources used for this contract:

- PyTorch `torchrun` docs: https://docs.pytorch.org/docs/2.9/elastic/run.html
- PyTorch rendezvous docs: https://docs.pytorch.org/docs/stable/elastic/rendezvous
- Hugging Face Accelerate launchers: https://huggingface.co/docs/accelerate/en/package_reference/launchers
- Slurm `sbatch`: https://slurm.schedmd.com/sbatch.html
- Slurm `srun`: https://slurm.schedmd.com/srun.html
