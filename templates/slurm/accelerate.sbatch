#!/usr/bin/env bash
#SBATCH --job-name=rdh-accelerate
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
NNODES="${SLURM_JOB_NUM_NODES:-${SLURM_NNODES:-1}}"
NODE_RANK="${SLURM_NODEID:-0}"
NPROC_PER_NODE="${SLURM_GPUS_ON_NODE:-8}"
NUM_PROCESSES="$((NNODES * NPROC_PER_NODE))"

mkdir -p logs checkpoints

srun --ntasks="${NNODES}" --ntasks-per-node=1 \
  accelerate launch \
    --num_machines "${NNODES}" \
    --num_processes "${NUM_PROCESSES}" \
    --machine_rank "${NODE_RANK}" \
    --main_process_ip "${MASTER_ADDR}" \
    --main_process_port "${MASTER_PORT}" \
    --rdzv_backend static \
    train.py \
    --checkpoint-dir checkpoints
