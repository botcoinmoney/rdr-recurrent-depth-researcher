from pathlib import Path

from rdharness.config import load_config, validate_config


def test_default_pipeline_config_is_valid():
    config = load_config()
    assert validate_config(config) == []


def test_default_pipeline_has_multiple_strategy_templates():
    config = load_config()
    templates = config["idea_generation"]["strategy_templates"]
    assert len(templates) >= 4
    assert all(template["title"] for template in templates)


def test_default_pipeline_has_grounding_and_knobs():
    config = load_config()
    assert len(config["grounding"]["prior_findings"]) >= 5
    assert len(config["recurrent_knobs"]["families"]) >= 5


def test_default_pipeline_file_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "configs" / "pipelines" / "default.yaml").exists()
