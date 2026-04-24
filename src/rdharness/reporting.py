from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .serialization import utc_now_iso

from .types import CycleReport


def render_cycle_markdown(report: CycleReport, config: dict[str, Any]) -> str:
    controls = config["grounding"]["evaluation_requirements"]
    findings = config["grounding"]["prior_findings"]
    knob_families = config["recurrent_knobs"]["families"]

    lines = [
        f"# Cycle {report['cycle']:03d}",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        "## Mission",
        config["mission"]["primary_question"],
        "",
        "## Cycle Summary",
        f"- Research items considered: {report['research_count']}",
        f"- Dataset/repo candidates considered: {report['dataset_count']}",
        f"- Ideas generated: {report['idea_count']}",
        f"- Runs attempted: {len(report['runs'])}",
        "",
        "## Required Controls",
    ]
    for item in controls:
        lines.append(f"- {item}")

    lines.extend(["", "## Grounding Findings"])
    for item in findings:
        lines.append(f"- {item['id']}: {item['lesson']}")

    lines.extend(["", "## Active Knob Families"])
    for item in knob_families:
        values = ", ".join(str(value) for value in item.get("candidate_values", []))
        lines.append(f"- {item['id']}: {item['description']} Candidate values: {values}")

    lines.extend(["", "## Run Outcomes"])
    if not report["runs"]:
        lines.append("- No runs were scheduled.")
    for run in report["runs"]:
        lines.append(
            f"- {run['title']} | dataset={run['dataset']} | score={run['score']} | status={run['metrics'].get('status')}"
        )

    best_run = report.get("best_run")
    lines.extend(["", "## Best Run"])
    if best_run:
        lines.append(
            f"- {best_run['title']} | dataset={best_run['dataset']} | score={best_run['score']} | run_dir={best_run['run_dir']}"
        )
    else:
        lines.append("- No best run selected.")

    lines.extend(["", "## Next Handoff"])
    if best_run:
        lines.append(
            f"- Continue from {best_run['run_dir']} only if it beats the no-adapter depth curve and the matched scramble control."
        )
    else:
        lines.append("- Configure a real experiment command and rerun the cycle.")

    return "\n".join(lines) + "\n"


def update_workspace_docs(workspace: Path, report: CycleReport, config: dict[str, Any]) -> None:
    reports_dir = workspace / "reports"
    cycle_md = reports_dir / f"cycle-{report['cycle']:03d}.md"
    cycle_md.write_text(render_cycle_markdown(report, config))

    findings_path = workspace / "findings.md"
    if not findings_path.exists():
        findings_path.write_text("# Findings Log\n\n")
    with findings_path.open("a") as handle:
        handle.write(f"## Cycle {report['cycle']:03d} - {report['generated_at']}\n\n")
        for run in report["runs"]:
            handle.write(
                f"- {run['title']} | dataset={run['dataset']} | score={run['score']} | status={run['metrics'].get('status')}\n"
            )
        handle.write("\n")

    handoff_path = workspace / "HANDOFF.md"
    handoff_payload = {
        "updated_at": utc_now_iso(),
        "latest_cycle": report["cycle"],
        "best_run": report.get("best_run"),
    }
    handoff_path.write_text(
        "# Handoff\n\n"
        "Use the latest cycle markdown and findings log first.\n\n"
        "```json\n"
        f"{json.dumps(handoff_payload, indent=2)}\n"
        "```\n"
    )
