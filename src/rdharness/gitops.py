from __future__ import annotations

import subprocess
from pathlib import Path


def ensure_git_repo(path: Path) -> None:
    if (path / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "checkout", "-b", "main"], cwd=path, check=True, capture_output=True, text=True)


def commit_workspace(path: Path, message: str) -> bool:
    if not (path / ".git").exists():
        return False

    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, text=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        return False
    subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, capture_output=True, text=True)
    return True
