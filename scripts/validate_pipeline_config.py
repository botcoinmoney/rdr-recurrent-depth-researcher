#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rdharness.config import load_config, validate_config


def main() -> int:
    config = load_config()
    failures = validate_config(config)
    if failures:
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Pipeline config validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
