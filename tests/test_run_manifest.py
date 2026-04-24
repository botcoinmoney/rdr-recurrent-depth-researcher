from pathlib import Path

import yaml


def test_run_manifest_includes_transfer_ladder_and_checklists():
    root = Path(__file__).resolve().parents[1]
    path = root / "configs" / "run_manifest.yaml"
    data = yaml.safe_load(path.read_text())

    assert data["version"] == 1
    assert data["mission"]["primary_question"]

    transfer_ladder = data["mission"]["transfer_ladder"]
    stages = [item["stage"] for item in transfer_ladder]
    assert stages == [
        "scenario_structural_fidelity",
        "real_multi_hop_transfer",
        "causal_transfer",
    ]

    required_sections = data["mission"]["required_run_sections"]
    assert "findings_log" in required_sections
    assert "eval_queue" in required_sections

    phase_checklists = data["mission"]["phase_checklists"]
    assert "pre_training" in phase_checklists
    assert "causal eval where applicable" in phase_checklists["per_variant"]
    assert "record ladder outcome" in phase_checklists["closeout"]

    stop_conditions = data["mission"]["stop_conditions"]
    assert any("multi-hop" in item for item in stop_conditions)
    assert any("causal" in item for item in stop_conditions)
