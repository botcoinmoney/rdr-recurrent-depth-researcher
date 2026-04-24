from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml

from .paths import repo_root
from .types import JSONObject, JSONValue


DEFAULT_CONFIG_PATH = repo_root() / "configs" / "pipelines" / "default.yaml"


def load_yaml(path: Path) -> JSONObject:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at {path}")
    return data


def load_config(path: str | Path | None = None) -> JSONObject:
    config_path = Path(path).resolve() if path else DEFAULT_CONFIG_PATH
    data = load_yaml(config_path)
    data["_config_path"] = str(config_path)
    return data


T = TypeVar("T")


def get_nested(mapping: JSONObject, dotted_key: str, default: T | None = None) -> JSONValue | T | None:
    current: JSONValue = mapping
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def validate_config(data: JSONObject) -> list[str]:
    failures: list[str] = []
    for key in (
        "version",
        "name",
        "mission",
        "research",
        "data_discovery",
        "grounding",
        "recurrent_knobs",
        "idea_generation",
        "execution",
        "ranking",
        "loop",
    ):
        if key not in data:
            failures.append(f"Missing top-level key: {key}")

    research_queries = get_nested(data, "research.queries", [])
    if not isinstance(research_queries, list) or not research_queries:
        failures.append("research.queries must contain at least one query")

    strategy_templates = get_nested(data, "idea_generation.strategy_templates", [])
    if not isinstance(strategy_templates, list) or not strategy_templates:
        failures.append("idea_generation.strategy_templates must contain at least one template")

    prior_findings = get_nested(data, "grounding.prior_findings", [])
    if not isinstance(prior_findings, list) or not prior_findings:
        failures.append("grounding.prior_findings must contain at least one finding")

    knob_families = get_nested(data, "recurrent_knobs.families", [])
    if not isinstance(knob_families, list) or not knob_families:
        failures.append("recurrent_knobs.families must contain at least one knob family")

    llm_provider = get_nested(data, "idea_generation.llm.provider", "none")
    if llm_provider not in {"none", "openai", "anthropic"}:
        failures.append("idea_generation.llm.provider must be one of: none, openai, anthropic")

    execution_mode = get_nested(data, "execution.mode", "builtin_research_pipeline")
    if execution_mode not in {"builtin_research_pipeline", "command"}:
        failures.append("execution.mode must be one of: builtin_research_pipeline, command")

    loop_sleep = get_nested(data, "loop.sleep_seconds", 0)
    if not isinstance(loop_sleep, int) or loop_sleep < 0:
        failures.append("loop.sleep_seconds must be a non-negative integer")

    return failures
