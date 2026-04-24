from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from .paths import ensure_dir, repo_root
from .types import default_workspace_state


WORKSPACE_DIRS = [
    "research",
    "datasets",
    "runs",
    "reports",
    "agent_prompts",
    "logs",
    "notes",
]

WORKSPACE_TEMPLATE_FILES = {
    "manual_data_sources.yaml": "manual_data_sources.yaml",
    "README.md": "WORKSPACE_README.md",
    "notes/next_actions.md": "next_actions.md",
    "findings.md": "findings.md",
    "HANDOFF.md": "HANDOFF.md",
    ".gitignore": ".gitignore",
    "data_recipes.yaml": "data_recipes.yaml",
    "agent_bootstrap.md": "agent_bootstrap.md",
}


def init_workspace(target: Path, config: dict, force: bool = False) -> None:
    target = target.resolve()
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"Workspace is not empty: {target}")

    ensure_dir(target)
    for relative in WORKSPACE_DIRS:
        ensure_dir(target / relative)

    templates_root = repo_root() / "templates" / "workspace"
    shutil.copy2(Path(config["_config_path"]).resolve(), target / "pipeline.yaml")
    for destination, template_name in WORKSPACE_TEMPLATE_FILES.items():
        (target / destination).write_text((templates_root / template_name).read_text())

    state = default_workspace_state(status="initialized")
    (target / "workspace_state.yaml").write_text(yaml.safe_dump(state, sort_keys=False))
