from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from .paths import repo_root
from .types import JSONObject


INSTALL_MATRIX_PATH = repo_root() / "configs" / "environment" / "install_matrix.yaml"
ENVIRONMENT_DIR = repo_root() / "configs" / "environment"


def _load_yaml_mapping(path: Path) -> JSONObject:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at {path}")
    return data


def load_install_matrix() -> JSONObject:
    return _load_yaml_mapping(INSTALL_MATRIX_PATH)


def load_environment_profile(profile: str) -> JSONObject:
    path = ENVIRONMENT_DIR / f"{profile}.yaml"
    if not path.exists():
        raise ValueError(f"Unknown environment profile: {profile}")
    data = _load_yaml_mapping(path)
    environment = data.get("environment")
    if not isinstance(environment, dict):
        raise ValueError(f"Missing environment section in {path}")
    return environment


def available_environment_profiles() -> list[str]:
    return sorted(path.stem for path in ENVIRONMENT_DIR.glob("*.yaml") if path.stem != "install_matrix")


def detect_environment_profile() -> str:
    if shutil.which("nvidia-smi") is None:
        return "cpu_local"
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"],
        check=True,
        capture_output=True,
        text=True,
    )
    count = len([line for line in result.stdout.splitlines() if line.strip()])
    if count <= 0:
        return "cpu_local"
    if count == 1:
        return "single_gpu"
    if count <= 8:
        return "multi_gpu"
    return "cluster_shared"


def _expand_value(value: str) -> str:
    return os.path.expanduser(os.path.expandvars(value))


def _resolve_path(value: str) -> str:
    expanded = Path(_expand_value(value))
    if expanded.is_absolute():
        return str(expanded)
    return str((repo_root() / expanded).resolve())


def resolve_install_plan(
    profile: str | None = None,
    *,
    torch_profile: str | None = None,
    include_dev: bool | None = None,
    venv_path: str | None = None,
) -> JSONObject:
    matrix = load_install_matrix()
    environment = load_environment_profile(profile) if profile else {}
    install_defaults = environment.get("install", {})

    selected_torch_profile = torch_profile or install_defaults.get("torch_profile", "cpu")
    torch_profiles = matrix.get("torch_profiles", {})
    if selected_torch_profile not in torch_profiles:
        raise ValueError(f"Unknown torch profile: {selected_torch_profile}")

    include_dev_packages = install_defaults.get("include_dev", True) if include_dev is None else include_dev
    selected_venv = venv_path or install_defaults.get("venv_path", ".venv")
    plan = {
        "profile": profile,
        "python_min": environment.get("python_min", matrix.get("python", {}).get("min")),
        "venv_path": _resolve_path(selected_venv),
        "pip_bootstrap_packages": list(matrix.get("pip_bootstrap_packages", [])),
        "base_packages": list(matrix.get("base_packages", [])),
        "dev_packages": list(matrix.get("dev_packages", [])) if include_dev_packages else [],
        "recommended_env": {
            key: _expand_value(str(value))
            for key, value in environment.get("recommended_env", {}).items()
        },
        "required_env": list(environment.get("required_env", [])),
        "torch_profile": selected_torch_profile,
        "torch_index_url": torch_profiles[selected_torch_profile]["index_url"],
        "torch_packages": list(torch_profiles[selected_torch_profile]["packages"]),
    }
    return plan


def install_commands(plan: JSONObject) -> list[list[str]]:
    venv_python = Path(plan["venv_path"]) / "bin" / "python"
    return [
        [sys.executable, "-m", "venv", plan["venv_path"]],
        [str(venv_python), "-m", "pip", "install", "--upgrade", *plan["pip_bootstrap_packages"]],
        [str(venv_python), "-m", "pip", "install", "--no-deps", "-e", str(repo_root())],
        [str(venv_python), "-m", "pip", "install", *plan["base_packages"]],
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--index-url",
            plan["torch_index_url"],
            *plan["torch_packages"],
        ],
        *(
            [[str(venv_python), "-m", "pip", "install", *plan["dev_packages"]]]
            if plan["dev_packages"]
            else []
        ),
    ]


def run_install_plan(plan: JSONObject, *, dry_run: bool = False) -> None:
    commands = install_commands(plan)
    for command in commands:
        if dry_run:
            print(shlex.join(command))
            continue
        subprocess.run(command, check=True)


def shell_exports(plan: JSONObject) -> list[str]:
    exports = [f'export VIRTUAL_ENV="{plan["venv_path"]}"', 'export PATH="$VIRTUAL_ENV/bin:$PATH"']
    for key, value in sorted(plan["recommended_env"].items()):
        exports.append(f'export {key}="{value}"')
    return exports
