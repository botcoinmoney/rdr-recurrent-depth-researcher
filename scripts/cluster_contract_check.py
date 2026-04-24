#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def _count_visible_devices() -> int | None:
    cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if cuda_visible:
        devices = [item for item in cuda_visible.split(",") if item.strip()]
        if devices:
            return len(devices)

    slurm_gpus = os.environ.get("SLURM_GPUS_ON_NODE", "").strip()
    if slurm_gpus.isdigit():
        return int(slurm_gpus)
    return None


def _resolve_master_addr() -> str | None:
    if os.environ.get("MASTER_ADDR"):
        return os.environ["MASTER_ADDR"]
    nodelist = os.environ.get("SLURM_JOB_NODELIST", "").strip()
    if not nodelist:
        return None
    try:
        completed = subprocess.run(
            ["scontrol", "show", "hostnames", nodelist],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    hosts = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return hosts[0] if hosts else None


def _resolve_master_port() -> int:
    if os.environ.get("MASTER_PORT", "").isdigit():
        return int(os.environ["MASTER_PORT"])
    job_id = os.environ.get("SLURM_JOB_ID", "0")
    digits = "".join(char for char in job_id if char.isdigit())
    offset = int(digits[-4:] or "0")
    return 20000 + (offset % 20000)


def build_report(launcher: str) -> dict[str, object]:
    slurm_detected = bool(os.environ.get("SLURM_JOB_ID"))
    master_addr = _resolve_master_addr()
    master_port = _resolve_master_port()
    node_rank = int(os.environ.get("SLURM_NODEID", "0"))
    num_nodes = int(
        os.environ.get("SLURM_JOB_NUM_NODES")
        or os.environ.get("SLURM_NNODES")
        or "1"
    )
    nproc_per_node = _count_visible_devices() or 1
    job_id = os.environ.get("SLURM_JOB_ID", "local")

    failures: list[str] = []
    warnings: list[str] = []
    if not slurm_detected:
        warnings.append("SLURM_JOB_ID is not set; this looks like a non-Slurm shell.")
    if not os.environ.get("SLURM_JOB_NODELIST"):
        warnings.append("SLURM_JOB_NODELIST is not set; MASTER_ADDR could not be derived from Slurm.")
    if slurm_detected and master_addr is None:
        failures.append("Could not resolve MASTER_ADDR from env or scontrol.")
    if launcher not in {"torchrun", "accelerate"}:
        failures.append(f"Unsupported launcher: {launcher}")

    exports = {
        "SLURM_EXPORT_ENV": "ALL",
        "MASTER_ADDR": master_addr or "<set-master-addr>",
        "MASTER_PORT": str(master_port),
        "RDZV_ID": f"rdh-{job_id}",
        "NNODES": str(num_nodes),
        "NODE_RANK": str(node_rank),
        "NPROC_PER_NODE": str(nproc_per_node),
    }

    torchrun_command = (
        "srun --ntasks=${NNODES} --ntasks-per-node=1 "
        "torchrun "
        "--nnodes=${NNODES} "
        "--nproc-per-node=${NPROC_PER_NODE} "
        "--node_rank=${NODE_RANK} "
        "--rdzv-id=${RDZV_ID} "
        "--rdzv-backend=c10d "
        "--rdzv-endpoint=${MASTER_ADDR}:${MASTER_PORT} "
        "--max-restarts=0 "
        "train.py"
    )
    accelerate_command = (
        "srun --ntasks=${NNODES} --ntasks-per-node=1 "
        "accelerate launch "
        "--num_machines ${NNODES} "
        "--num_processes $((NNODES * NPROC_PER_NODE)) "
        "--machine_rank ${NODE_RANK} "
        "--main_process_ip ${MASTER_ADDR} "
        "--main_process_port ${MASTER_PORT} "
        "--rdzv_backend static "
        "train.py"
    )

    recovery_notes = [
        "Do not nest launchers. Use either torchrun or accelerate as the distributed entrypoint for the job step.",
        "Keep checkpoint naming independent of rank identity; elastic rendezvous does not guarantee stable ranks.",
        "Treat scheduler requeue and torch elastic restart as different failure paths. Requeue should resume from durable checkpoints.",
        "Use a unique rendezvous id per allocation or restart lineage to avoid colliding with stale stores.",
        "Persist logs and checkpoints on shared durable storage rather than node-local scratch alone.",
    ]

    return {
        "launcher": launcher,
        "slurm_detected": slurm_detected,
        "exports": exports,
        "torchrun_command": torchrun_command,
        "accelerate_command": accelerate_command,
        "warnings": warnings,
        "failures": failures,
        "recovery_notes": recovery_notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check and print a concrete Slurm launch contract for torchrun or accelerate."
    )
    parser.add_argument(
        "--launcher",
        choices=["torchrun", "accelerate"],
        default="torchrun",
        help="Primary launcher to validate and print first.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "shell"],
        default="shell",
        help="Output format.",
    )
    args = parser.parse_args()

    report = build_report(args.launcher)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print("# Suggested exports")
        for key, value in report["exports"].items():
            print(f'export {key}="{value}"')
        print()
        print("# Suggested command")
        print(report[f"{args.launcher}_command"])
        if report["warnings"]:
            print()
            print("# Warnings")
            for item in report["warnings"]:
                print(f"- {item}")
        if report["failures"]:
            print()
            print("# Failures")
            for item in report["failures"]:
                print(f"- {item}")
        print()
        print("# Recovery notes")
        for item in report["recovery_notes"]:
            print(f"- {item}")

    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
