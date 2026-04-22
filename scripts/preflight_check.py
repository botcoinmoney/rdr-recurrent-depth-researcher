#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


REQUIRED_DOCS = [
    "START_HERE.md",
    "README.md",
    "RULES.md",
    "ORCHESTRATOR_RULES.md",
    "docs/PRIOR_EXPERIMENT_FINDINGS.md",
    "docs/CANONICAL_TESTING_METHODS.md",
    "docs/DEPENDENCIES_AND_SOURCES.md",
    "docs/COMMON_FAILURE_MODES.md",
]


def check_path(root: Path, rel_path: str, failures: list[str]) -> None:
    if not (root / rel_path).exists():
        failures.append(f"Missing required path: {rel_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Repo root to validate")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []

    if not root.exists():
        failures.append(f"Root does not exist: {root}")
    if failures:
        print("\n".join(failures))
        return 1

    for rel in REQUIRED_DOCS:
        check_path(root, rel, failures)

    findings = root / "findings.md"
    if root.name.startswith("botcoin-lt-run-") or (root / "handoff").exists():
        if not findings.exists():
            failures.append("Live run repo should contain findings.md")

    for tool in ("git", "gh", "python3"):
        if shutil.which(tool) is None:
            failures.append(f"Missing required executable: {tool}")

    for env_name in ("HF_HOME", "TRANSFORMERS_CACHE"):
        if not os.environ.get(env_name):
            failures.append(f"Environment variable not set: {env_name}")

    if failures:
        print("Preflight failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Preflight passed for {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

