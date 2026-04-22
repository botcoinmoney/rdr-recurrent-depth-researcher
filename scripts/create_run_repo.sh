#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <repo-name>"
  exit 1
fi

REPO_NAME="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNS_DIR="${HOME}/runs"
TARGET_DIR="${RUNS_DIR}/${REPO_NAME}"

mkdir -p "${RUNS_DIR}"

if [[ -e "${TARGET_DIR}" ]]; then
  echo "target already exists: ${TARGET_DIR}"
  exit 1
fi

mkdir -p "${TARGET_DIR}"
cp -R "${ROOT_DIR}/templates/." "${TARGET_DIR}/"
mkdir -p "${TARGET_DIR}/handoff"
cp "${ROOT_DIR}/README.md" "${TARGET_DIR}/handoff/README.md"
cp "${ROOT_DIR}/RULES.md" "${TARGET_DIR}/handoff/RULES.md"
cp "${ROOT_DIR}/ORCHESTRATOR_RULES.md" "${TARGET_DIR}/handoff/ORCHESTRATOR_RULES.md"
cp -R "${ROOT_DIR}/docs" "${TARGET_DIR}/handoff/docs"
cp -R "${ROOT_DIR}/configs" "${TARGET_DIR}/handoff/configs"
cp -R "${ROOT_DIR}/scripts" "${TARGET_DIR}/handoff/scripts"

cd "${TARGET_DIR}"
git init
git checkout -b main

if ! gh repo view "botcoinmoney/${REPO_NAME}" >/dev/null 2>&1; then
  gh repo create "botcoinmoney/${REPO_NAME}" --private --source . --remote origin --push
else
  git remote add origin "git@github.com:botcoinmoney/${REPO_NAME}.git"
fi

git add .
git commit -m "Initialize live experiment repo"
git push -u origin main

echo "Created live run repo at ${TARGET_DIR}"

