from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .dataops import load_recipe_manifest, materialize_recipe
from .types import CatalogItem, JSONObject, MaterializedVariantStats
from .serialization import save_json, utc_now_iso


@dataclass
class RunResult:
    run_dir: Path
    command: str
    executed: bool
    returncode: int | None
    metrics: JSONObject
    stdout_path: Path
    stderr_path: Path


def materialize_command(template: str, context: JSONObject) -> str:
    command = template
    for key, value in context.items():
        command = command.replace(f"{{{{{key}}}}}", str(value))
    return command


def run_experiment(
    idea: JSONObject,
    execution_config: JSONObject,
    runs_dir: Path,
    workspace: Path,
    catalog: list[CatalogItem],
) -> RunResult:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = "-".join(str(idea.get("title", "idea")).lower().split())[:60]
    run_dir = runs_dir / f"{timestamp}-{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    metrics_path = run_dir / execution_config.get("metrics_file", "metrics.json")
    plan_path = run_dir / "plan.json"
    save_json(plan_path, {"idea": idea, "generated_at": utc_now_iso()})

    mode = execution_config.get("mode", "builtin_research_pipeline")
    if mode == "builtin_research_pipeline":
        metrics, command, returncode = run_builtin_research_pipeline(
            idea=idea,
            execution_config=execution_config,
            run_dir=run_dir,
            workspace=workspace,
            catalog=catalog,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )
        save_json(metrics_path, metrics)
        return RunResult(
            run_dir=run_dir,
            command=command,
            executed=returncode is not None,
            returncode=returncode,
            metrics=metrics,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    template = execution_config.get("experiment_command", "").strip()
    if not template:
        metrics: JSONObject = {"status": "planned_only", "positive_signal": 0.0}
        save_json(metrics_path, metrics)
        return RunResult(
            run_dir=run_dir,
            command="",
            executed=False,
            returncode=None,
            metrics=metrics,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    command = materialize_command(
        template,
        {
            "run_dir": run_dir,
            "dataset": idea.get("dataset", ""),
            "title": idea.get("title", ""),
            "approach": idea.get("approach", ""),
            "controls": json.dumps(idea.get("controls", [])),
            "knobs": json.dumps(idea.get("knob_assignments", {})),
            "python": sys.executable,
        },
    )
    completed = subprocess.run(command, shell=True, text=True, capture_output=True)
    stdout_path.write_text(completed.stdout)
    stderr_path.write_text(completed.stderr)

    metrics: JSONObject = {}
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
    metrics.setdefault("status", "completed" if completed.returncode == 0 else "failed")

    return RunResult(
        run_dir=run_dir,
        command=command,
        executed=True,
        returncode=completed.returncode,
        metrics=metrics,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )


def run_builtin_research_pipeline(
    idea: JSONObject,
    execution_config: JSONObject,
    run_dir: Path,
    workspace: Path,
    catalog: list[CatalogItem],
    stdout_path: Path,
    stderr_path: Path,
) -> tuple[JSONObject, str, int | None]:
    commands_cfg = execution_config.get("commands", {})
    train_template = str(commands_cfg.get("train", "")).strip()
    eval_template = str(commands_cfg.get("eval", "")).strip()
    probe_template = str(commands_cfg.get("probe", "")).strip()
    if not train_template or not eval_template:
        return {"status": "planned_only", "positive_signal": 0.0}, "", None

    source = resolve_dataset_source(idea.get("dataset", ""), catalog, workspace)
    if source is None:
        return {
            "status": "failed",
            "failure_reason": f"Could not resolve local dataset source for {idea.get('dataset')}",
        }, "", 1

    recipe_manifest = load_recipe_manifest(workspace / execution_config.get("data_recipe_manifest", "data_recipes.yaml"))
    materialized = materialize_variants(
        source_path=Path(source["path"]).resolve(),
        run_dir=run_dir,
        recipe_manifest=recipe_manifest,
        variant_plan=execution_config.get("variant_plan", []),
        candidate_recipe=select_candidate_recipe(idea, execution_config),
    )

    logs: list[str] = []
    errors: list[str] = []
    jobs_dir = run_dir / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)

    base_model = resolve_base_model(execution_config)
    depths = execution_config.get("depth_sweep", [4, 8, 16, 32])
    eval_conditions = execution_config.get("eval_conditions", ["default", "evidence_ablated"])

    trained_variants: dict[str, str] = {"baseline": base_model}
    status_code = 0

    for variant in execution_config.get("variant_plan", []):
        role = variant["role"]
        if not variant.get("train", False):
            continue
        model_dir = jobs_dir / role / "model"
        model_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = jobs_dir / role / "train_metrics.json"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        command = materialize_command(
            train_template,
            {
                "python": sys.executable,
                "run_dir": run_dir,
                "workspace": workspace,
                "base_model": base_model,
                "dataset_path": materialized[role]["dataset_path"],
                "output_dir": model_dir,
                "variant_name": role,
                "title": idea.get("title", ""),
                "approach": idea.get("approach", ""),
                "controls": json.dumps(idea.get("controls", [])),
                "knobs": json.dumps(idea.get("knob_assignments", {})),
                "metrics_path": metrics_path,
            },
        )
        completed = subprocess.run(command, shell=True, text=True, capture_output=True)
        logs.append(f"$ {command}\n{completed.stdout}")
        errors.append(f"$ {command}\n{completed.stderr}")
        if completed.returncode != 0:
            status_code = completed.returncode
        trained_variants[role] = str(model_dir)

    probe_scores: list[float] = []
    eval_scores: dict[str, dict[str, float]] = {}
    command_log: list[str] = []
    for variant in execution_config.get("variant_plan", []):
        role = variant["role"]
        if not variant.get("evaluate", variant.get("model_variant", True)):
            continue
        model_path = trained_variants.get(role, base_model)
        if not model_path:
            continue
        eval_scores[role] = {}
        probe_dataset_path = materialized.get("eval_default", materialized["baseline"])["dataset_path"]

        if probe_template:
            probe_path = jobs_dir / role / "probe_metrics.json"
            probe_path.parent.mkdir(parents=True, exist_ok=True)
            probe_command = materialize_command(
                probe_template,
                {
                    "python": sys.executable,
                    "run_dir": run_dir,
                    "workspace": workspace,
                    "model_path": model_path,
                    "dataset_path": probe_dataset_path,
                    "variant_name": role,
                    "title": idea.get("title", ""),
                    "approach": idea.get("approach", ""),
                    "controls": json.dumps(idea.get("controls", [])),
                    "knobs": json.dumps(idea.get("knob_assignments", {})),
                    "metrics_path": probe_path,
                },
            )
            completed = subprocess.run(probe_command, shell=True, text=True, capture_output=True)
            logs.append(f"$ {probe_command}\n{completed.stdout}")
            errors.append(f"$ {probe_command}\n{completed.stderr}")
            command_log.append(probe_command)
            if probe_path.exists():
                probe_metrics = json.loads(probe_path.read_text())
                if isinstance(probe_metrics.get("probe_auc"), (int, float)):
                    probe_scores.append(float(probe_metrics["probe_auc"]))

        for condition in eval_conditions:
            condition_key = f"eval_{condition}"
            dataset_path = materialized.get(condition_key, materialized["baseline"])["dataset_path"]
            for depth in depths:
                metrics_path = jobs_dir / role / f"eval-{condition}-r{depth}.json"
                metrics_path.parent.mkdir(parents=True, exist_ok=True)
                eval_command = materialize_command(
                    eval_template,
                    {
                        "python": sys.executable,
                        "run_dir": run_dir,
                        "workspace": workspace,
                        "model_path": model_path,
                        "dataset_path": dataset_path,
                        "variant_name": role,
                        "condition": condition,
                        "depth": depth,
                        "title": idea.get("title", ""),
                        "approach": idea.get("approach", ""),
                        "controls": json.dumps(idea.get("controls", [])),
                        "knobs": json.dumps(idea.get("knob_assignments", {})),
                        "metrics_path": metrics_path,
                    },
                )
                completed = subprocess.run(eval_command, shell=True, text=True, capture_output=True)
                logs.append(f"$ {eval_command}\n{completed.stdout}")
                errors.append(f"$ {eval_command}\n{completed.stderr}")
                command_log.append(eval_command)
                if completed.returncode != 0:
                    status_code = completed.returncode
                    continue
                if not metrics_path.exists():
                    continue
                metrics = json.loads(metrics_path.read_text())
                score = select_eval_score(metrics)
                eval_scores[role][f"{condition}@R{depth}"] = score

    stdout_path.write_text("\n\n".join(logs))
    stderr_path.write_text("\n\n".join(errors))
    metrics = aggregate_builtin_metrics(eval_scores, probe_scores)
    metrics["materialized_variants"] = materialized
    metrics["status"] = "completed" if status_code == 0 else "failed"
    metrics["command_count"] = len(command_log)
    return metrics, "\n".join(command_log), status_code


def select_candidate_recipe(idea: JSONObject, execution_config: JSONObject) -> str:
    approach = str(idea.get("approach", "")).lower()
    overrides = execution_config.get("candidate_recipe_overrides", {})
    for key, value in overrides.items():
        if key in approach:
            return str(value)
    return str(execution_config.get("default_candidate_recipe", "identity"))


def resolve_base_model(execution_config: JSONObject) -> str:
    explicit = str(execution_config.get("base_model", "")).strip()
    if explicit:
        return explicit

    preset_name = str(execution_config.get("base_model_preset", "")).strip()
    presets = execution_config.get("base_model_presets", {})
    if not preset_name or not isinstance(presets, dict):
        return ""

    preset = presets.get(preset_name, {})
    if not isinstance(preset, dict):
        return ""
    return str(preset.get("pointer", "")).strip()


def materialize_variants(
    source_path: Path,
    run_dir: Path,
    recipe_manifest: JSONObject,
    variant_plan: list[JSONObject],
    candidate_recipe: str,
) -> dict[str, MaterializedVariantStats]:
    datasets_dir = run_dir / "datasets"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    materialized: dict[str, MaterializedVariantStats] = {}

    for variant in variant_plan:
        role = variant["role"]
        recipe_name = candidate_recipe if variant.get("recipe_from_idea", False) else str(variant["recipe"])
        output_path = datasets_dir / f"{role}.jsonl"
        stats = materialize_recipe(
            source_path=source_path,
            output_path=output_path,
            recipe_name=recipe_name,
            recipe_manifest=recipe_manifest,
        )
        stats["dataset_path"] = str(output_path)
        materialized[role] = stats
    return materialized


def resolve_dataset_source(dataset_name: str, catalog: list[CatalogItem], workspace: Path) -> CatalogItem | None:
    for item in catalog:
        if item.get("name") == dataset_name and item.get("path"):
            return item

    manual_manifest = workspace / "manual_data_sources.yaml"
    if manual_manifest.exists():
        data = yaml_safe_load(manual_manifest)
        for item in data.get("sources", []):
            if item.get("name") == dataset_name and item.get("path"):
                candidate = workspace / str(item["path"])
                if candidate.exists():
                    return {"name": dataset_name, "path": str(candidate)}
                path = Path(str(item["path"])).expanduser()
                if path.exists():
                    return {"name": dataset_name, "path": str(path.resolve())}
    return None


def yaml_safe_load(path: Path) -> JSONObject:
    import yaml

    data = yaml.safe_load(path.read_text()) or {}
    return data if isinstance(data, dict) else {}


def select_eval_score(metrics: JSONObject) -> float:
    for key in ("composite_score", "accuracy", "em", "f1", "score"):
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def aggregate_builtin_metrics(eval_scores: dict[str, dict[str, float]], probe_scores: list[float]) -> JSONObject:
    baseline_default = [score for key, score in eval_scores.get("baseline", {}).items() if key.startswith("default@R")]
    candidate_default = [score for key, score in eval_scores.get("candidate", {}).items() if key.startswith("default@R")]
    scramble_default = [score for key, score in eval_scores.get("scramble_control", {}).items() if key.startswith("default@R")]
    evidence_ablated = [score for key, score in eval_scores.get("candidate", {}).items() if key.startswith("evidence_ablated@R")]

    baseline_best = max(baseline_default) if baseline_default else 0.0
    candidate_best = max(candidate_default) if candidate_default else 0.0
    scramble_best = max(scramble_default) if scramble_default else 0.0
    ablated_best = max(evidence_ablated) if evidence_ablated else 0.0

    deep_absolute_gain = candidate_best - baseline_best
    scramble_gap = candidate_best - scramble_best
    evidence_gap = candidate_best - ablated_best
    probe_auc = sum(probe_scores) / len(probe_scores) if probe_scores else 0.0
    positive_signal = max(0.0, deep_absolute_gain) + max(0.0, scramble_gap) + max(0.0, evidence_gap)

    return {
        "positive_signal": round(positive_signal, 4),
        "deep_absolute_gain": round(deep_absolute_gain, 4),
        "scramble_gap": round(scramble_gap, 4),
        "evidence_gap": round(evidence_gap, 4),
        "probe_auc": round(probe_auc, 4),
        "baseline_best_score": round(baseline_best, 4),
        "candidate_best_score": round(candidate_best, 4),
        "scramble_best_score": round(scramble_best, 4),
        "eval_scores": eval_scores,
    }


def score_run(metrics: JSONObject, ranking_config: JSONObject) -> float:
    higher = ranking_config.get("higher_is_better", [])
    lower = ranking_config.get("lower_is_better", [])
    score = 0.0
    for key in higher:
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            score += float(value)
    for key in lower:
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            score -= float(value)
    if metrics.get("status") == "planned_only":
        score -= 1.0
    return round(score, 3)
