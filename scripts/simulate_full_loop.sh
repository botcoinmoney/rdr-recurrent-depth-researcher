#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SIM_ROOT="$(mktemp -d)"
RUNS_DIR="${SIM_ROOT}/runs"
WORKSPACE="${SIM_ROOT}/workspace"
SCRIPTS_DIR="${SIM_ROOT}/scripts"

export HF_HOME="${SIM_ROOT}/hf-cache"
export TRANSFORMERS_CACHE="${SIM_ROOT}/hf-cache"
export HUGGINGFACE_HUB_CACHE="${SIM_ROOT}/hf-cache"

mkdir -p "${HF_HOME}" "${SCRIPTS_DIR}"

echo "== ROOT PREFLIGHT =="
python3 "${ROOT_DIR}/scripts/preflight_check.py" --root "${ROOT_DIR}"

echo
echo "== LOCAL LIVE RUN REPO CREATION =="
bash "${ROOT_DIR}/scripts/create_run_repo.sh" --local-only --runs-dir "${RUNS_DIR}" rdh-run-sim
RUN_REPO="${RUNS_DIR}/rdh-run-sim"
python3 "${RUN_REPO}/handoff/scripts/preflight_check.py" --root "${RUN_REPO}"

echo
echo "== WORKSPACE INIT =="
python3 -m rdharness.cli init-workspace --workspace "${WORKSPACE}"

cat > "${WORKSPACE}/datasets/toy.jsonl" <<'EOF'
{"question":"q1","evidence":["e1","e2"],"answer":"a1","reasoning":["r1","r2"]}
{"question":"q2","evidence":["e3","e4"],"answer":"a2","reasoning":["r3","r4"]}
EOF

cat > "${WORKSPACE}/manual_data_sources.yaml" <<EOF
sources:
  - kind: local_dataset
    name: toy-local
    path: ${WORKSPACE}/datasets/toy.jsonl
EOF

cat > "${SCRIPTS_DIR}/train.py" <<'EOF'
import argparse, json, pathlib

p = argparse.ArgumentParser()
p.add_argument("--train-data")
p.add_argument("--output-dir")
p.add_argument("--metrics-path")
p.add_argument("--base-model")
p.add_argument("--knobs")
a = p.parse_args()
pathlib.Path(a.output_dir).mkdir(parents=True, exist_ok=True)
records = pathlib.Path(a.train_data).read_text().strip().splitlines()
json.dump(
    {"loss": 0.42, "records": len(records), "base_model": a.base_model},
    open(a.metrics_path, "w"),
)
EOF

cat > "${SCRIPTS_DIR}/eval.py" <<'EOF'
import argparse, json

p = argparse.ArgumentParser()
p.add_argument("--model")
p.add_argument("--eval-data")
p.add_argument("--depth", type=int)
p.add_argument("--condition")
p.add_argument("--metrics-path")
a = p.parse_args()
score = a.depth / 100.0
if a.condition == "evidence_ablated":
    score -= 0.05
if "scramble_control" in a.model:
    score -= 0.03
if "candidate" in a.model:
    score += 0.04
json.dump(
    {
        "accuracy": score,
        "composite_score": score,
        "condition": a.condition,
        "depth": a.depth,
    },
    open(a.metrics_path, "w"),
)
EOF

cat > "${SCRIPTS_DIR}/probe.py" <<'EOF'
import argparse, json

p = argparse.ArgumentParser()
p.add_argument("--model")
p.add_argument("--eval-data")
p.add_argument("--metrics-path")
a = p.parse_args()
score = 0.72 if "candidate" in a.model else 0.61
json.dump({"probe_auc": score}, open(a.metrics_path, "w"))
EOF

python3 - <<EOF
from pathlib import Path
import yaml

workspace = Path("${WORKSPACE}")
pipeline = yaml.safe_load((workspace / "pipeline.yaml").read_text())
pipeline["research"]["queries"] = ["recurrent depth transformer reasoning"]
pipeline["research"]["max_results_per_query"] = 1
pipeline["research"]["max_saved_papers"] = 2
pipeline["data_discovery"]["queries"] = []
pipeline["data_discovery"]["providers"] = {"huggingface": False, "github": False}
pipeline["execution"]["ideas_per_cycle"] = 1
pipeline["execution"]["depth_sweep"] = [4, 8, 16]
pipeline["loop"]["sleep_seconds"] = 0
pipeline["execution"]["commands"]["train"] = "{{python}} ${SCRIPTS_DIR}/train.py --base-model {{base_model}} --train-data {{dataset_path}} --output-dir {{output_dir}} --knobs '{{knobs}}' --metrics-path {{metrics_path}}"
pipeline["execution"]["commands"]["eval"] = "{{python}} ${SCRIPTS_DIR}/eval.py --model {{model_path}} --eval-data {{dataset_path}} --depth {{depth}} --condition {{condition}} --metrics-path {{metrics_path}}"
pipeline["execution"]["commands"]["probe"] = "{{python}} ${SCRIPTS_DIR}/probe.py --model {{model_path}} --eval-data {{dataset_path}} --metrics-path {{metrics_path}}"
(workspace / "pipeline.yaml").write_text(yaml.safe_dump(pipeline, sort_keys=False))
EOF

echo
echo "== WORKSPACE VALIDATION =="
python3 -m rdharness.cli --config "${WORKSPACE}/pipeline.yaml" validate-config
python3 -m rdharness.cli materialize-data --workspace "${WORKSPACE}" --source "${WORKSPACE}/datasets/toy.jsonl" --recipe evidence_slice --output "${WORKSPACE}/datasets/toy-evidence-slice.jsonl"
python3 -m rdharness.cli discover-data --workspace "${WORKSPACE}"
python3 -m rdharness.cli refresh-research --workspace "${WORKSPACE}" || true

echo
echo "== SINGLE CYCLE =="
python3 -m rdharness.cli run-cycle --workspace "${WORKSPACE}" >/dev/null

echo
echo "== CONTINUOUS LOOP RESUME =="
python3 -m rdharness.cli loop --workspace "${WORKSPACE}" --max-cycles 2

echo
echo "== FINAL SUMMARY =="
python3 - <<EOF
from pathlib import Path
import subprocess
import yaml

workspace = Path("${WORKSPACE}")
state = yaml.safe_load((workspace / "workspace_state.yaml").read_text())
reports = sorted((workspace / "reports").glob("cycle-*.json"))

print("workspace_state:", state)
print("report_count:", len(reports))
print("latest_report:", reports[-1].name if reports else "none")
print("recent_findings:")
for line in (workspace / "findings.md").read_text().splitlines()[:12]:
    print(line)
print("recent_commits:")
print(
    subprocess.run(
        ["git", "-C", str(workspace), "log", "--oneline", "-n", "4"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
)
EOF

echo "SIM_ROOT=${SIM_ROOT}"
echo "RUN_REPO=${RUN_REPO}"
echo "WORKSPACE=${WORKSPACE}"
