from __future__ import annotations

import subprocess
import time
import warnings
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import requests
import yaml

from .discovery import (
    discover_github_repos,
    discover_huggingface_datasets,
    discover_local_data,
    discover_manual_sources,
    save_catalog,
)
from .execution import run_experiment, score_run
from .gitops import commit_workspace, ensure_git_repo
from .ideas import generate_ideas, save_ideas
from .reporting import update_workspace_docs
from .research import fetch_arxiv_papers, load_research_snapshot, save_research_snapshot
from .serialization import save_json, utc_now_iso
from .types import CycleReport, RunSummary, WorkspaceState, default_workspace_state


def refresh_research(config: dict[str, Any], workspace: Path) -> list[dict[str, Any]]:
    research_cfg = config["research"]
    try:
        papers = fetch_arxiv_papers(
            queries=research_cfg["queries"],
            max_results=int(research_cfg.get("max_results_per_query", 6)),
        )
    except (requests.RequestException, ElementTree.ParseError) as exc:
        warnings.warn(f"Research refresh failed; saving empty snapshot instead: {exc}", stacklevel=2)
        papers = []
    snapshot_path = workspace / "research" / "latest_research.json"
    save_research_snapshot(papers[: int(research_cfg.get("max_saved_papers", 15))], snapshot_path)
    return load_research_snapshot(snapshot_path)


def discover_data(config: dict[str, Any], workspace: Path) -> list[dict[str, Any]]:
    discovery_cfg = config["data_discovery"]
    items: list[dict[str, Any]] = []
    manual_manifest = workspace / discovery_cfg.get("manual_manifest", "manual_data_sources.yaml")
    items.extend(discover_manual_sources(manual_manifest))
    items.extend(discover_local_data(discovery_cfg.get("local_globs", []), workspace))
    if discovery_cfg.get("providers", {}).get("huggingface", False):
        items.extend(
            discover_huggingface_datasets(
                discovery_cfg.get("queries", []),
                limit=int(discovery_cfg.get("max_results_per_query", 5)),
            )
        )
    if discovery_cfg.get("providers", {}).get("github", False):
        items.extend(
            discover_github_repos(
                discovery_cfg.get("queries", []),
                limit=int(discovery_cfg.get("max_results_per_query", 5)),
            )
        )
    save_catalog(items, workspace / "datasets" / "catalog.json")
    return items


def _load_state(workspace: Path) -> WorkspaceState:
    state_path = workspace / "workspace_state.yaml"
    if not state_path.exists():
        return default_workspace_state()
    data = yaml.safe_load(state_path.read_text()) or {}
    if not isinstance(data, dict):
        return default_workspace_state()
    return {
        "workspace_version": int(data.get("workspace_version", 1)),
        "status": str(data.get("status", "unknown")),
        "active_cycle": int(data.get("active_cycle", 0)),
        "best_run": data.get("best_run"),
    }


def _save_state(workspace: Path, state: WorkspaceState) -> None:
    (workspace / "workspace_state.yaml").write_text(yaml.safe_dump(state, sort_keys=False))


def run_cycle(config: dict[str, Any], workspace: Path) -> CycleReport:
    workspace = workspace.resolve()
    state = _load_state(workspace)
    cycle_index = int(state.get("active_cycle", 0)) + 1

    research = refresh_research(config, workspace)
    datasets = discover_data(config, workspace)
    ideas = generate_ideas(config, research=research, datasets=datasets, prompts_dir=workspace / "agent_prompts")
    save_ideas(ideas, workspace / "reports" / f"ideas-cycle-{cycle_index:03d}.json")

    selected = ideas[: int(config["execution"].get("ideas_per_cycle", 2))]
    run_summaries: list[RunSummary] = []
    best_score = None
    best_run: RunSummary | None = None
    for idea in selected:
        result = run_experiment(
            idea,
            execution_config=config["execution"],
            runs_dir=workspace / "runs",
            workspace=workspace,
            catalog=datasets,
        )
        score = score_run(result.metrics, config["ranking"])
        summary: RunSummary = {
            "title": idea.get("title"),
            "dataset": idea.get("dataset"),
            "command": result.command,
            "executed": result.executed,
            "returncode": result.returncode,
            "metrics": result.metrics,
            "score": score,
            "run_dir": str(result.run_dir),
        }
        run_summaries.append(summary)
        if best_score is None or score > best_score:
            best_score = score
            best_run = summary

    report: CycleReport = {
        "generated_at": utc_now_iso(),
        "cycle": cycle_index,
        "research_count": len(research),
        "dataset_count": len(datasets),
        "idea_count": len(ideas),
        "runs": run_summaries,
        "best_run": best_run,
    }
    report_path = workspace / "reports" / f"cycle-{cycle_index:03d}.json"
    save_json(report_path, report)
    update_workspace_docs(workspace, report, config)

    state["active_cycle"] = cycle_index
    state["status"] = "running"
    if best_run:
        state["best_run"] = best_run
    _save_state(workspace, state)

    git_cfg = config["loop"].get("git", {})
    try:
        if git_cfg.get("ensure_repo", True):
            ensure_git_repo(workspace)
        if git_cfg.get("auto_commit", True):
            prefix = git_cfg.get("commit_message_prefix", "rdh cycle")
            commit_workspace(workspace, f"{prefix} {cycle_index:03d}")
    except (OSError, subprocess.CalledProcessError) as exc:
        warnings.warn(f"Git automation skipped after external command failure: {exc}", stacklevel=2)
    return report


def loop(config: dict[str, Any], workspace: Path, max_cycles: int | None = None) -> None:
    configured_max = int(config["loop"].get("max_cycles", 0))
    cycle_limit = max_cycles if max_cycles is not None else configured_max
    cycle_count = 0
    while True:
        run_cycle(config, workspace)
        cycle_count += 1
        if cycle_limit and cycle_count >= cycle_limit:
            return
        sleep_seconds = int(config["loop"].get("sleep_seconds", 300))
        time.sleep(sleep_seconds)
