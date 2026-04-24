from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config, validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rdh", description="Standalone recurrent-depth autoresearch harness")
    parser.add_argument("--config", default=None, help="Path to pipeline YAML config")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init-workspace", help="Create a standalone research workspace")
    init_cmd.add_argument("--workspace", required=True, help="Target workspace directory")
    init_cmd.add_argument("--force", action="store_true", help="Allow initializing into a non-empty directory")

    validate_cmd = subparsers.add_parser("validate-config", help="Validate the pipeline config")
    validate_cmd.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    refresh_cmd = subparsers.add_parser("refresh-research", help="Pull latest arXiv research snapshot")
    refresh_cmd.add_argument("--workspace", required=True)

    data_cmd = subparsers.add_parser("discover-data", help="Refresh the dataset and repo catalog")
    data_cmd.add_argument("--workspace", required=True)

    materialize_cmd = subparsers.add_parser("materialize-data", help="Materialize a dataset variant from a recipe")
    materialize_cmd.add_argument("--workspace", required=True)
    materialize_cmd.add_argument("--source", required=True, help="Path to a local dataset file")
    materialize_cmd.add_argument("--recipe", required=True, help="Recipe name from data_recipes.yaml")
    materialize_cmd.add_argument("--output", required=True, help="Output path for the transformed dataset")

    cycle_cmd = subparsers.add_parser("run-cycle", help="Run one end-to-end ideation and experiment cycle")
    cycle_cmd.add_argument("--workspace", required=True)

    loop_cmd = subparsers.add_parser("loop", help="Run the continuous research loop")
    loop_cmd.add_argument("--workspace", required=True)
    loop_cmd.add_argument("--max-cycles", type=int, default=None)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    workspace_arg = getattr(args, "workspace", None)
    config_path = args.config
    if config_path is None and workspace_arg:
        candidate = Path(workspace_arg).resolve() / "pipeline.yaml"
        if candidate.exists():
            config_path = candidate
    config = load_config(config_path)

    if args.command == "validate-config":
        failures = validate_config(config)
        if args.json:
            print(json.dumps({"ok": not failures, "failures": failures}, indent=2))
        else:
            if failures:
                for failure in failures:
                    print(f"- {failure}")
            else:
                print("Config validated.")
        return 0 if not failures else 1

    workspace = Path(workspace_arg or ".").resolve()

    if args.command == "init-workspace":
        from .workspace import init_workspace

        init_workspace(workspace, config=config, force=args.force)
        print(f"Initialized workspace at {workspace}")
        return 0
    if args.command == "refresh-research":
        from .orchestrator import refresh_research

        papers = refresh_research(config, workspace)
        print(f"Saved {len(papers)} research items to {workspace / 'research' / 'latest_research.json'}")
        return 0
    if args.command == "discover-data":
        from .orchestrator import discover_data

        items = discover_data(config, workspace)
        print(f"Saved {len(items)} catalog entries to {workspace / 'datasets' / 'catalog.json'}")
        return 0
    if args.command == "materialize-data":
        from .dataops import load_recipe_manifest, materialize_recipe

        recipe_manifest = load_recipe_manifest(workspace / config["execution"].get("data_recipe_manifest", "data_recipes.yaml"))
        stats = materialize_recipe(
            source_path=Path(args.source).resolve(),
            output_path=Path(args.output).resolve(),
            recipe_name=args.recipe,
            recipe_manifest=recipe_manifest,
        )
        print(json.dumps(stats, indent=2))
        return 0
    if args.command == "run-cycle":
        from .orchestrator import run_cycle

        report = run_cycle(config, workspace)
        print(json.dumps(report, indent=2))
        return 0
    if args.command == "loop":
        from .orchestrator import loop

        loop(config, workspace, max_cycles=args.max_cycles)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
