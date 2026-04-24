#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage: create_run_repo.sh [--local-only] [--runs-dir PATH] [--visibility private|public] <repo-name>

Create a live run repository from the bundled templates and handoff snapshot.

Options:
  --local-only           Initialize the git repo and checkpoint locally without creating a GitHub repo.
  --runs-dir PATH        Parent directory to create the live run repo under. Defaults to $HOME/runs.
  --visibility VIS       GitHub repo visibility when not using --local-only. Defaults to private.
  -h, --help             Show this help text.
EOF
}

local_only=0
runs_dir="${HOME}/runs"
visibility="private"
repo_name=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local-only)
      local_only=1
      shift
      ;;
    --runs-dir)
      if [[ $# -lt 2 ]]; then
        echo "missing value for --runs-dir" >&2
        exit 1
      fi
      runs_dir="$2"
      shift 2
      ;;
    --visibility)
      if [[ $# -lt 2 ]]; then
        echo "missing value for --visibility" >&2
        exit 1
      fi
      visibility="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -n "$repo_name" ]]; then
        echo "unexpected extra argument: $1" >&2
        usage
        exit 1
      fi
      repo_name="$1"
      shift
      ;;
  esac
done

if [[ -z "$repo_name" ]]; then
  usage
  exit 1
fi

if [[ "$visibility" != "private" && "$visibility" != "public" ]]; then
  echo "visibility must be 'private' or 'public'" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${runs_dir}/${repo_name}"

mkdir -p "${runs_dir}"

if [[ -e "${TARGET_DIR}" ]]; then
  echo "target already exists: ${TARGET_DIR}"
  exit 1
fi

mkdir -p "${TARGET_DIR}"
cp -R "${ROOT_DIR}/templates/." "${TARGET_DIR}/"
cp "${ROOT_DIR}/configs/run_manifest.yaml" "${TARGET_DIR}/run_manifest.yaml"
mkdir -p "${TARGET_DIR}/handoff"
cp "${ROOT_DIR}/START_HERE.md" "${TARGET_DIR}/handoff/START_HERE.md"
cp "${ROOT_DIR}/README.md" "${TARGET_DIR}/handoff/README.md"
cp "${ROOT_DIR}/RULES.md" "${TARGET_DIR}/handoff/RULES.md"
cp "${ROOT_DIR}/ORCHESTRATOR_RULES.md" "${TARGET_DIR}/handoff/ORCHESTRATOR_RULES.md"
cp -R "${ROOT_DIR}/docs" "${TARGET_DIR}/handoff/docs"
cp -R "${ROOT_DIR}/configs" "${TARGET_DIR}/handoff/configs"
cp -R "${ROOT_DIR}/scripts" "${TARGET_DIR}/handoff/scripts"

cd "${TARGET_DIR}"
git init
git checkout -b main

if [[ $local_only -eq 1 ]]; then
  "${ROOT_DIR}/scripts/checkpoint_commit_push.sh" --message "Initialize live experiment repo" --no-push
  echo "Created local-only live run repo at ${TARGET_DIR}"
  exit 0
fi

if ! gh repo view "botcoinmoney/${repo_name}" >/dev/null 2>&1; then
  gh repo create "botcoinmoney/${repo_name}" "--${visibility}" --source . --remote origin
else
  git remote add origin "https://github.com/botcoinmoney/${repo_name}.git"
fi

"${ROOT_DIR}/scripts/checkpoint_commit_push.sh" --message "Initialize live experiment repo"

echo "Created live run repo at ${TARGET_DIR}"
