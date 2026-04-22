from pathlib import Path

import yaml


def test_strategy_matrix_contains_five_grounded_strategies():
    root = Path(__file__).resolve().parents[1]
    path = root / "configs" / "strategies" / "strategy_matrix.yaml"
    data = yaml.safe_load(path.read_text())

    strategies = data["strategies"]
    assert len(strategies) == 5

    for strategy in strategies:
        assert strategy["why_this_exists"]
        assert strategy["grounded_evidence"]["papers"]
        assert strategy["grounded_evidence"]["local_findings"]
        assert strategy["budget_gpu_hours"] > 0


def test_self_contained_docs_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "docs" / "PRIOR_EXPERIMENT_FINDINGS.md",
        root / "docs" / "DEPENDENCIES_AND_SOURCES.md",
    ]
    for path in required:
        assert path.exists(), f"Missing required self-contained doc: {path}"

