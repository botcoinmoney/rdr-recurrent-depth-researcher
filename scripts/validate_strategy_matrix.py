#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml


REQUIRED_TOP_KEYS = {"version", "global_framing", "strategies"}
REQUIRED_STRATEGY_KEYS = {
    "id",
    "name",
    "order",
    "priority",
    "hypothesis",
    "why_this_exists",
    "grounded_evidence",
    "budget_gpu_hours",
    "metrics",
    "win_condition",
    "fail_interpretation",
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "configs" / "strategies" / "strategy_matrix.yaml"
    data = yaml.safe_load(path.read_text())

    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        raise SystemExit(f"Missing top-level keys: {sorted(missing)}")

    strategies = data["strategies"]
    if not isinstance(strategies, list) or len(strategies) != 5:
        raise SystemExit("Expected exactly 5 first-wave strategies")

    seen_ids = set()
    seen_orders = set()
    for strategy in strategies:
        missing_strategy = REQUIRED_STRATEGY_KEYS - strategy.keys()
        if missing_strategy:
            raise SystemExit(
                f"Strategy {strategy.get('id', '<unknown>')} missing keys: {sorted(missing_strategy)}"
            )
        if strategy["id"] in seen_ids:
            raise SystemExit(f"Duplicate strategy id: {strategy['id']}")
        if strategy["order"] in seen_orders:
            raise SystemExit(f"Duplicate strategy order: {strategy['order']}")
        seen_ids.add(strategy["id"])
        seen_orders.add(strategy["order"])

        if not strategy["why_this_exists"]:
            raise SystemExit(f"Strategy {strategy['id']} has empty rationale")
        if not strategy["grounded_evidence"].get("papers"):
            raise SystemExit(f"Strategy {strategy['id']} must cite at least one paper")
        if not strategy["grounded_evidence"].get("local_findings"):
            raise SystemExit(f"Strategy {strategy['id']} must cite at least one local finding")
        if strategy["budget_gpu_hours"] <= 0:
            raise SystemExit(f"Strategy {strategy['id']} must have positive budget")

    print("Strategy matrix validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

