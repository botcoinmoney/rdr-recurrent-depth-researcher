#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_DOCS = [
    "START_HERE.md",
    "README.md",
    "RULES.md",
    "ORCHESTRATOR_RULES.md",
    "docs/RESEARCH_REFRESH_2026.md",
    "docs/PRIOR_EXPERIMENT_FINDINGS.md",
    "docs/CANONICAL_TESTING_METHODS.md",
    "docs/DEPENDENCIES_AND_SOURCES.md",
    "docs/GPU_OPTIMIZATION_CHECKLIST.md",
    "docs/COMMON_FAILURE_MODES.md",
]

REQUIRED_HELPERS = [
    "scripts/checkpoint_commit_push.sh",
    "scripts/gpu_status.py",
    "scripts/setup_env.py",
]


def check_path(root: Path, rel_path: str, failures: list[str]) -> None:
    if not (root / rel_path).exists():
        failures.append(f"Missing required path: {rel_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Repo root to validate")
    parser.add_argument(
        "--check-gpu",
        action="store_true",
        help="Validate that at least one GPU is visible via nvidia-smi",
    )
    parser.add_argument(
        "--check-torch",
        action="store_true",
        help="Validate that torch imports cleanly in the current Python environment",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []

    if not root.exists():
        failures.append(f"Root does not exist: {root}")
    if failures:
        print("\n".join(failures))
        return 1

    docs_root = root / "handoff" if (root / "handoff").exists() else root

    for rel in REQUIRED_DOCS:
        check_path(docs_root, rel, failures)
    for rel in REQUIRED_HELPERS:
        check_path(docs_root, rel, failures)

    findings = root / "findings.md"
    run_manifest = root / "run_manifest.yaml"
    if root.name.startswith("rdh-run-") or (root / "handoff").exists():
        if not findings.exists():
            failures.append("Live run repo should contain findings.md")
        if not run_manifest.exists():
            failures.append("Live run repo should contain run_manifest.yaml")

    for tool in ("git", "gh", "python3"):
        if shutil.which(tool) is None:
            failures.append(f"Missing required executable: {tool}")

    for env_name in ("HF_HOME", "TRANSFORMERS_CACHE"):
        if not os.environ.get(env_name):
            failures.append(f"Environment variable not set: {env_name}")

    if args.check_gpu:
        if shutil.which("nvidia-smi") is None:
            failures.append("Missing required executable: nvidia-smi")
        else:
            try:
                output = subprocess.run(
                    ["nvidia-smi", "-L"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            except (OSError, subprocess.CalledProcessError) as exc:
                failures.append(f"Unable to query GPUs: {exc}")
            else:
                visible = [line for line in output.splitlines() if line.strip()]
                if not visible:
                    failures.append("No GPUs visible via nvidia-smi")

    if args.check_torch:
        try:
            subprocess.run(
                ["python3", "-c", "import torch; print(torch.__version__)"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            failures.append(f"Unable to import torch: {exc}")

    if failures:
        print("Preflight failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Preflight passed for {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
