from __future__ import annotations

import json
import random
import re
from copy import deepcopy
from pathlib import Path

import yaml

from .types import JSONObject, JSONValue, MaterializedVariantStats, RecipeConfig, RecipeManifest


COMMON_EVIDENCE_KEYS = {
    "evidence",
    "context",
    "documents",
    "docs",
    "passages",
    "supporting_facts",
    "support",
    "retrieved_context",
}
COMMON_REASONING_KEYS = {"reasoning", "steps", "chain_of_thought", "cot", "trace"}
COMMON_QUESTION_KEYS = {"question", "prompt", "query", "instruction"}
COMMON_ANSWER_KEYS = {"answer", "target", "label", "output"}
COMMON_WRONG_KEYS = {"incorrect_answer", "wrong_answer", "negative_answer", "failed_answer"}


def load_recipe_manifest(path: Path) -> RecipeManifest:
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in recipe manifest: {path}")
    return data


def read_records(path: Path) -> list[JSONObject]:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".json"}:
        if suffix == ".jsonl":
            records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        else:
            payload = json.loads(path.read_text())
            records = payload if isinstance(payload, list) else payload.get("records", [])
        return [record for record in records if isinstance(record, dict)]
    raise ValueError(f"Unsupported local dataset format for built-in transforms: {path}")


def write_records(path: Path, records: list[JSONObject]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


def materialize_recipe(
    source_path: Path,
    output_path: Path,
    recipe_name: str,
    recipe_manifest: RecipeManifest,
    seed: int = 0,
) -> MaterializedVariantStats:
    records = read_records(source_path)
    recipes = recipe_manifest.get("recipes", {})
    recipe_cfg = recipes.get(recipe_name)
    if not isinstance(recipe_cfg, dict):
        raise KeyError(f"Unknown recipe: {recipe_name}")

    transformed = [apply_recipe(record, recipe_cfg, seed + index) for index, record in enumerate(records)]
    transformed = [record for record in transformed if record]
    write_records(output_path, transformed)
    return {
        "recipe": recipe_name,
        "source_path": str(source_path),
        "output_path": str(output_path),
        "records_in": len(records),
        "records_out": len(transformed),
    }


def apply_recipe(record: JSONObject, recipe_cfg: RecipeConfig, seed: int) -> JSONObject:
    mode = recipe_cfg.get("mode", "identity")
    if mode == "identity":
        return deepcopy(record)
    if mode == "scramble_preserve_format":
        return scramble_record(record, seed=seed)
    if mode == "evidence_ablate":
        return ablate_evidence(record)
    if mode == "evidence_slice":
        return slice_evidence(record, max_items=int(recipe_cfg.get("max_items", 1)))
    if mode == "minimal_correction":
        return minimal_correction(record)
    if mode == "boundary_markers":
        return add_boundary_markers(record, marker=str(recipe_cfg.get("marker", "<hop>")))
    if mode == "contrastive_correction":
        return contrastive_correction(record)
    raise KeyError(f"Unsupported recipe mode: {mode}")


def scramble_record(record: JSONObject, seed: int) -> JSONObject:
    rng = random.Random(seed)
    cloned = deepcopy(record)
    for key, value in list(cloned.items()):
        if isinstance(value, str):
            tokens = value.split()
            rng.shuffle(tokens)
            cloned[key] = " ".join(tokens)
        elif isinstance(value, list) and value and all(isinstance(item, str) for item in value):
            shuffled = value[:]
            rng.shuffle(shuffled)
            cloned[key] = shuffled
    return cloned


def ablate_evidence(record: JSONObject) -> JSONObject:
    cloned = deepcopy(record)
    for key in list(cloned.keys()):
        if key.lower() in COMMON_EVIDENCE_KEYS:
            value = cloned[key]
            cloned[key] = [] if isinstance(value, list) else ""
    return cloned


def slice_evidence(record: JSONObject, max_items: int = 1) -> JSONObject:
    cloned = deepcopy(record)
    for key in list(cloned.keys()):
        if key.lower() not in COMMON_EVIDENCE_KEYS:
            continue
        value = cloned[key]
        if isinstance(value, list):
            cloned[key] = value[:max_items]
        elif isinstance(value, str):
            sentences = re.split(r"(?<=[.!?])\s+", value.strip())
            cloned[key] = " ".join(sentences[:max_items]).strip()
    return cloned


def minimal_correction(record: JSONObject) -> JSONObject:
    question = first_matching_value(record, COMMON_QUESTION_KEYS)
    answer = first_matching_value(record, COMMON_ANSWER_KEYS)
    wrong = first_matching_value(record, COMMON_WRONG_KEYS)
    evidence = first_matching_value(record, COMMON_EVIDENCE_KEYS)
    result: JSONObject = {}
    if question is not None:
        result["question"] = question
    if wrong is not None:
        result["incorrect_answer"] = wrong
    if answer is not None:
        result["answer"] = answer
    if evidence is not None:
        result["evidence"] = evidence
    if not result:
        return deepcopy(record)
    return result


def add_boundary_markers(record: JSONObject, marker: str) -> JSONObject:
    cloned = deepcopy(record)
    for key in list(cloned.keys()):
        if key.lower() in COMMON_REASONING_KEYS and isinstance(cloned[key], list):
            cloned[key] = [f"{marker} {item}" if isinstance(item, str) else item for item in cloned[key]]
        elif key.lower() in COMMON_REASONING_KEYS and isinstance(cloned[key], str):
            parts = [part.strip() for part in cloned[key].split("\n") if part.strip()]
            cloned[key] = "\n".join(f"{marker} {part}" for part in parts)
    return cloned


def contrastive_correction(record: JSONObject) -> JSONObject:
    cloned = minimal_correction(record)
    if "incorrect_answer" not in cloned:
        wrong = first_matching_value(record, COMMON_REASONING_KEYS)
        if wrong is not None:
            cloned["incorrect_answer"] = wrong
    return cloned


def first_matching_value(record: JSONObject, keys: set[str]) -> JSONValue:
    for key, value in record.items():
        if key.lower() in keys:
            return deepcopy(value)
    return None
