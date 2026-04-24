#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class GpuRecord:
    index: int
    uuid: str
    name: str
    memory_total: int
    memory_used: int
    util_gpu: int
    util_mem: int
    processes: tuple[str, ...]

    @property
    def load_key(self) -> tuple[int, int, int, int]:
        return (self.memory_used, self.util_gpu, len(self.processes), self.index)


def run_nvidia_smi(args: list[str]) -> str:
    if shutil.which("nvidia-smi") is None:
        raise SystemExit("nvidia-smi is not available on this machine")
    result = subprocess.run(
        ["nvidia-smi", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def parse_csv_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    reader = csv.reader(line for line in text.splitlines() if line.strip())
    for row in reader:
        cleaned = [item.strip() for item in row]
        if cleaned:
            rows.append(cleaned)
    return rows


def load_profile(profile: str | None) -> tuple[int | None, int]:
    if not profile:
        return None, 0

    path = REPO_ROOT / "configs" / "environment" / f"{profile}.yaml"
    if not path.exists():
        raise SystemExit(f"unknown environment profile: {profile}")

    data = yaml.safe_load(path.read_text())
    environment = data.get("environment", {})
    gpus = environment.get("gpus")
    protected = environment.get("protected_defaults", {})
    reserve = 1 if protected.get("keep_one_gpu_available_for_eval_or_output_gate") else 0
    reserve = max(reserve, 1 if protected.get("keep_gpu0_for_eval_or_output_gate") else 0)
    return int(gpus) if gpus is not None else None, reserve


def collect_gpu_records() -> list[GpuRecord]:
    gpu_rows = parse_csv_rows(
        run_nvidia_smi(
            [
                "--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu,utilization.memory",
                "--format=csv,noheader,nounits",
            ]
        )
    )

    process_rows: dict[str, list[str]] = defaultdict(list)
    try:
        raw_processes = run_nvidia_smi(
            [
                "--query-compute-apps=gpu_uuid,pid,process_name,used_memory",
                "--format=csv,noheader,nounits",
            ]
        )
    except subprocess.CalledProcessError as exc:
        warnings.warn(f"Could not read GPU process details; continuing without them: {exc}", stacklevel=2)
        raw_processes = ""

    for row in parse_csv_rows(raw_processes):
        if len(row) < 4:
            continue
        gpu_uuid, pid, process_name, used_memory = row[:4]
        process_rows[gpu_uuid].append(f"{pid}:{process_name}:{used_memory}MiB")

    records: list[GpuRecord] = []
    for row in gpu_rows:
        if len(row) < 7:
            continue
        index, uuid, name, memory_total, memory_used, util_gpu, util_mem = row[:7]
        records.append(
            GpuRecord(
                index=int(index),
                uuid=uuid,
                name=name,
                memory_total=int(memory_total),
                memory_used=int(memory_used),
                util_gpu=int(util_gpu),
                util_mem=int(util_mem),
                processes=tuple(process_rows.get(uuid, ())),
            )
        )
    return records


def fmt_gb(megabytes: int) -> str:
    return f"{megabytes / 1024:.1f}GiB"


def print_status(records: list[GpuRecord]) -> None:
    print(f"visible_gpus: {len(records)}")
    print("gpu_status:")
    print("  idx  name                      used/total      util  mem_util  processes")
    for record in records:
        processes = ", ".join(record.processes) if record.processes else "-"
        print(
            f"  {record.index:>3}  {record.name[:24]:<24}  {fmt_gb(record.memory_used):>5}/{fmt_gb(record.memory_total):<5}"
            f"  {record.util_gpu:>4}%  {record.util_mem:>7}%  {processes}"
        )


def print_allocation(records: list[GpuRecord], reserve: int, count: int | None, profile_limit: int | None) -> None:
    budget = min(len(records), profile_limit) if profile_limit is not None else len(records)
    reserved = min(max(reserve, 0), budget)
    available = max(0, budget - reserved)
    if count is None:
        count = available
    else:
        count = min(max(count, 0), available)

    selected = sorted(records, key=lambda record: record.load_key)[:count]
    selected_ids = ",".join(str(record.index) for record in selected)
    selected_phrase = selected_ids if selected_ids else "<none>"

    print("allocation:")
    print(f"  reserve: {reserved}")
    print(f"  request: {count}")
    if profile_limit is not None:
        print(f"  profile_gpu_budget: {profile_limit}")
        if len(records) != profile_limit:
            print(f"  profile_warning: visible_gpus={len(records)}")
    print(f"  suggested_cuda_visible_devices: {selected_phrase}")
    print(f"  export CUDA_VISIBLE_DEVICES={selected_ids}")
    if selected:
        print("  selected_gpu_load:")
        for record in selected:
            print(
                f"    {record.index} ({record.name}): used={fmt_gb(record.memory_used)} "
                f"util={record.util_gpu}% processes={len(record.processes)}"
            )
    else:
        print("  selected_gpu_load: []")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show current GPU status and suggest a lightweight allocation."
    )
    parser.add_argument("--profile", help="Environment profile from configs/environment")
    parser.add_argument("--allocate", action="store_true", help="Print an allocation suggestion")
    parser.add_argument("--count", type=int, help="Number of GPUs to include in the allocation")
    parser.add_argument(
        "--reserve",
        type=int,
        help="Number of GPUs to hold back from the suggestion; defaults to repo profile guidance",
    )
    args = parser.parse_args()

    profile_limit, profile_reserve = load_profile(args.profile)
    records = collect_gpu_records()

    print_status(records)

    if args.allocate:
        reserve = args.reserve if args.reserve is not None else profile_reserve
        if args.reserve is None and reserve == 0 and len(records) > 1:
            reserve = 1
        print_allocation(records, reserve=reserve, count=args.count, profile_limit=profile_limit)

    return 0


if __name__ == "__main__":
    sys.exit(main())
