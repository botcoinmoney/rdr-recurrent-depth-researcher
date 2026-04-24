#!/usr/bin/env bash
#SBATCH --job-name=rdh-torchrun
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=8
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

export SLURM_EXPORT_ENV=ALL
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME}"
export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HOME}"

MASTER_ADDR="$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)"
MASTER_PORT="${MASTER_PORT:-$((20000 + (SLURM_JOB_ID % 20000)))}"
RDZV_ID="${RDZV_ID:-rdh-${SLURM_JOB_ID}}"
NNODES="${SLURM_JOB_NUM_NODES:-${SLURM_NNODES:-1}}"
NODE_RANK="${SLURM_NODEID:-0}"
NPROC_PER_NODE="${SLURM_GPUS_ON_NODE:-8}"

mkdir -p logs checkpoints

srun --ntasks="${NNODES}" --ntasks-per-node=1 \
  torchrun \
    --nnodes="${NNODES}" \
    --nproc-per-node="${NPROC_PER_NODE}" \
    --node_rank="${NODE_RANK}" \
    --rdzv-id="${RDZV_ID}" \
    --rdzv-backend=c10d \
    --rdzv-endpoint="${MASTER_ADDR}:${MASTER_PORT}" \
    --max-restarts=0 \
    train.py \
    --checkpoint-dir checkpoints
