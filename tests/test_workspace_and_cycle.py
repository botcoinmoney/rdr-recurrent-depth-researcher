import json
import subprocess
from pathlib import Path

import pytest
import yaml

from rdharness.dataops import materialize_recipe
from rdharness.orchestrator import refresh_research, run_cycle
from rdharness.workspace import init_workspace


def test_init_workspace_creates_expected_files(tmp_path):
    config = {
        "_config_path": str(tmp_path / "pipeline-template.yaml"),
        "mission": {"primary_question": "test"},
    }
    (tmp_path / "pipeline-template.yaml").write_text("version: 1\nname: test\n")

    workspace = tmp_path / "workspace"
    init_workspace(workspace, config=config, force=False)

    assert (workspace / "pipeline.yaml").exists()
    assert (workspace / "manual_data_sources.yaml").exists()
    assert (workspace / "workspace_state.yaml").exists()
    assert (workspace / "findings.md").exists()
    assert (workspace / "HANDOFF.md").exists()
    assert (workspace / "data_recipes.yaml").exists()
    assert (workspace / "agent_bootstrap.md").exists()
    state = yaml.safe_load((workspace / "workspace_state.yaml").read_text())
    assert state["active_cycle"] == 0


def test_materialize_recipe_supports_evidence_slice(tmp_path):
    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps({"question": "q", "evidence": ["a", "b", "c"], "answer": "x"}) + "\n"
    )
    recipes = {
        "recipes": {
            "evidence_slice": {
                "mode": "evidence_slice",
                "max_items": 1,
            }
        }
    }
    output = tmp_path / "out.jsonl"
    stats = materialize_recipe(source, output, "evidence_slice", recipes)
    assert stats["records_out"] == 1
    record = json.loads(output.read_text().strip())
    assert record["evidence"] == ["a"]


def test_run_cycle_with_builtin_pipeline_executes_real_commands(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for relative in ("research", "datasets", "runs", "reports", "agent_prompts", "logs", "notes"):
        (workspace / relative).mkdir()

    dataset_path = workspace / "datasets" / "toy.jsonl"
    dataset_path.write_text(
        "\n".join(
            [
                json.dumps({"question": "q1", "evidence": ["e1", "e2"], "answer": "a1", "reasoning": ["r1", "r2"]}),
                json.dumps({"question": "q2", "evidence": ["e3", "e4"], "answer": "a2", "reasoning": ["r3", "r4"]}),
            ]
        )
        + "\n"
    )

    (workspace / "manual_data_sources.yaml").write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "kind": "local_dataset",
                        "name": "toy-local",
                        "path": str(dataset_path),
                    }
                ]
            },
            sort_keys=False,
        )
    )
    (workspace / "workspace_state.yaml").write_text("workspace_version: 1\nstatus: initialized\nactive_cycle: 0\n")
    (workspace / "data_recipes.yaml").write_text(
        yaml.safe_dump(
            {
                "recipes": {
                    "identity": {"mode": "identity"},
                    "scramble_preserve_format": {"mode": "scramble_preserve_format"},
                    "evidence_ablate": {"mode": "evidence_ablate"},
                    "evidence_slice": {"mode": "evidence_slice", "max_items": 1},
                }
            },
            sort_keys=False,
        )
    )
    (workspace / "findings.md").write_text("# Findings Log\n\n")
    (workspace / "HANDOFF.md").write_text("# Handoff\n")

    train_script = tmp_path / "train.py"
    train_script.write_text(
        "\n".join(
            [
                "import argparse, json, pathlib",
                "p=argparse.ArgumentParser()",
                "p.add_argument('--train-data'); p.add_argument('--output-dir'); p.add_argument('--metrics-path')",
                "p.add_argument('--base-model'); p.add_argument('--knobs')",
                "a=p.parse_args()",
                "pathlib.Path(a.output_dir).mkdir(parents=True, exist_ok=True)",
                "records = pathlib.Path(a.train_data).read_text().strip().splitlines()",
                "json.dump({'loss': 0.5, 'records': len(records)}, open(a.metrics_path,'w'))",
            ]
        )
    )
    eval_script = tmp_path / "eval.py"
    eval_script.write_text(
        "\n".join(
            [
                "import argparse, json, pathlib",
                "p=argparse.ArgumentParser()",
                "p.add_argument('--model'); p.add_argument('--eval-data'); p.add_argument('--depth', type=int); p.add_argument('--condition'); p.add_argument('--metrics-path')",
                "a=p.parse_args()",
                "text = pathlib.Path(a.eval_data).read_text()",
                "score = a.depth / 100.0",
                "if a.condition == 'evidence_ablated': score -= 0.05",
                "if 'scramble_control' in a.model: score -= 0.03",
                "if 'candidate' in a.model: score += 0.04",
                "json.dump({'accuracy': score, 'composite_score': score}, open(a.metrics_path,'w'))",
            ]
        )
    )
    probe_script = tmp_path / "probe.py"
    probe_script.write_text(
        "\n".join(
            [
                "import argparse, json",
                "p=argparse.ArgumentParser()",
                "p.add_argument('--model'); p.add_argument('--eval-data'); p.add_argument('--metrics-path')",
                "a=p.parse_args()",
                "score = 0.72 if 'candidate' in a.model else 0.61",
                "json.dump({'probe_auc': score}, open(a.metrics_path,'w'))",
            ]
        )
    )

    config = {
        "mission": {"primary_question": "Which idea works?"},
        "research": {"queries": ["recurrent depth"], "max_results_per_query": 2, "max_saved_papers": 4},
        "data_discovery": {
            "manual_manifest": "manual_data_sources.yaml",
            "local_globs": ["datasets/**/*.jsonl"],
            "queries": [],
            "providers": {"huggingface": False, "github": False},
        },
        "grounding": {
            "prior_findings": [{"id": "f1", "lesson": "test lesson"}],
            "evaluation_requirements": ["compare against baseline depth curve"],
        },
        "recurrent_knobs": {
            "families": [
                {"id": "loop_depth_schedule", "description": "depth schedule", "candidate_values": ["fixed_8", "fixed_16"]},
                {"id": "halting_policy", "description": "act", "candidate_values": ["fixed_loops", "act_099"]},
            ]
        },
        "idea_generation": {
            "roles": ["theorist"],
            "max_ideas": 3,
            "llm": {"provider": "none"},
            "strategy_templates": [
                {
                    "title": "Idea A",
                    "hypothesis_template": "{dataset} with {paper}",
                    "approach": "local evidence snippets",
                    "expected_signal": "lift",
                    "risk": "none",
                }
            ],
        },
        "execution": {
            "mode": "builtin_research_pipeline",
            "ideas_per_cycle": 1,
            "base_model": "base-model",
            "metrics_file": "metrics.json",
            "data_recipe_manifest": "data_recipes.yaml",
            "default_candidate_recipe": "evidence_slice",
            "candidate_recipe_overrides": {"local evidence snippets": "evidence_slice"},
            "depth_sweep": [4, 8],
            "eval_conditions": ["default", "evidence_ablated"],
            "variant_plan": [
                {"role": "baseline", "recipe": "identity", "train": False, "model_variant": True},
                {"role": "candidate", "recipe_from_idea": True, "train": True, "model_variant": True},
                {"role": "scramble_control", "recipe": "scramble_preserve_format", "train": True, "model_variant": True},
                {"role": "eval_default", "recipe": "identity", "train": False, "model_variant": False, "evaluate": False},
                {"role": "eval_evidence_ablated", "recipe": "evidence_ablate", "train": False, "model_variant": False, "evaluate": False},
            ],
            "commands": {
                "train": f"{{{{python}}}} {train_script} --base-model {{{{base_model}}}} --train-data {{{{dataset_path}}}} --output-dir {{{{output_dir}}}} --knobs '{{{{knobs}}}}' --metrics-path {{{{metrics_path}}}}",
                "eval": f"{{{{python}}}} {eval_script} --model {{{{model_path}}}} --eval-data {{{{dataset_path}}}} --depth {{{{depth}}}} --condition {{{{condition}}}} --metrics-path {{{{metrics_path}}}}",
                "probe": f"{{{{python}}}} {probe_script} --model {{{{model_path}}}} --eval-data {{{{dataset_path}}}} --metrics-path {{{{metrics_path}}}}",
            },
        },
        "ranking": {"higher_is_better": ["positive_signal", "scramble_gap"], "lower_is_better": ["loss"]},
        "loop": {"sleep_seconds": 0, "max_cycles": 1, "git": {"ensure_repo": False, "auto_commit": False}},
    }

    monkeypatch.setattr(
        "rdharness.orchestrator.refresh_research",
        lambda _config, _workspace: [
            {
                "title": "Loop, Think, & Generalize",
                "published": "2026-04-09T00:00:00Z",
                "relevance_score": 4.2,
            }
        ],
    )

    report = run_cycle(config, workspace)
    assert report["cycle"] == 1
    assert report["idea_count"] == 1
    assert len(report["runs"]) == 1
    run = report["runs"][0]
    assert run["executed"] is True
    assert run["returncode"] == 0
    assert run["metrics"]["candidate_best_score"] > run["metrics"]["baseline_best_score"]
    assert run["metrics"]["scramble_gap"] > 0

    saved_report = json.loads((workspace / "reports" / "cycle-001.json").read_text())
    assert saved_report["cycle"] == 1
    assert (workspace / "reports" / "cycle-001.md").exists()
    assert "Cycle 001" in (workspace / "findings.md").read_text()


def test_refresh_research_does_not_hide_internal_errors(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    (workspace / "research").mkdir(parents=True)
    config = {
        "research": {
            "queries": ["recurrent depth"],
            "max_results_per_query": 2,
            "max_saved_papers": 4,
        }
    }

    monkeypatch.setattr(
        "rdharness.orchestrator.fetch_arxiv_papers",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("bug in parser pipeline")),
    )

    with pytest.raises(RuntimeError, match="bug in parser pipeline"):
        refresh_research(config, workspace)


def test_run_cycle_warns_when_git_automation_fails(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    for relative in ("research", "datasets", "runs", "reports", "agent_prompts", "logs", "notes"):
        (workspace / relative).mkdir()

    (workspace / "manual_data_sources.yaml").write_text("sources: []\n")
    (workspace / "workspace_state.yaml").write_text("workspace_version: 1\nstatus: initialized\nactive_cycle: 0\n")
    (workspace / "findings.md").write_text("# Findings Log\n\n")
    (workspace / "HANDOFF.md").write_text("# Handoff\n")

    config = {
        "mission": {"primary_question": "Which idea works?"},
        "research": {"queries": [], "max_results_per_query": 2, "max_saved_papers": 4},
        "data_discovery": {
            "manual_manifest": "manual_data_sources.yaml",
            "local_globs": [],
            "queries": [],
            "providers": {"huggingface": False, "github": False},
        },
        "grounding": {"prior_findings": [], "evaluation_requirements": []},
        "recurrent_knobs": {"families": []},
        "idea_generation": {
            "roles": ["theorist"],
            "max_ideas": 1,
            "llm": {"provider": "none"},
            "strategy_templates": [
                {
                    "title": "Idea A",
                    "hypothesis_template": "x",
                    "approach": "manual",
                    "expected_signal": "lift",
                    "risk": "none",
                }
            ],
        },
        "execution": {
            "mode": "builtin_research_pipeline",
            "ideas_per_cycle": 1,
            "commands": {},
        },
        "ranking": {"higher_is_better": ["positive_signal"], "lower_is_better": ["loss"]},
        "loop": {"sleep_seconds": 0, "max_cycles": 1, "git": {"ensure_repo": True, "auto_commit": True}},
    }

    monkeypatch.setattr("rdharness.orchestrator.refresh_research", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("rdharness.orchestrator.ensure_git_repo", lambda _workspace: None)

    def fail_commit(_workspace: Path, _message: str) -> bool:
        raise subprocess.CalledProcessError(1, ["git", "commit"], stderr="commit failed")

    monkeypatch.setattr("rdharness.orchestrator.commit_workspace", fail_commit)

    with pytest.warns(UserWarning, match="Git automation skipped after external command failure"):
        report = run_cycle(config, workspace)

    assert report["cycle"] == 1
