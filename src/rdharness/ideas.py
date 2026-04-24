from __future__ import annotations

from pathlib import Path

from .llm import build_adapter, parse_json_block
from .serialization import dedupe_by_preference, save_timestamped_json
from .types import CatalogItem, JSONObject


ROLE_BRIEFS = {
    "theorist": "Propose experiment directions that most directly test recurrent depth training hypotheses.",
    "data_scout": "Focus on promising datasets, corpora, and repos that fit the research findings.",
    "skeptic": "Stress-test the ideas for shortcut learning, dataset leakage, weak transfer, and measurement blind spots.",
}


def build_prompt(
    role: str,
    mission: str,
    research: list[JSONObject],
    datasets: list[CatalogItem],
    grounding: JSONObject,
    knob_families: list[JSONObject],
    max_ideas: int,
) -> str:
    top_research = research[:6]
    top_datasets = datasets[:8]
    lines = [
        f"You are the {role} subagent in a recurrent-depth autoresearch harness.",
        ROLE_BRIEFS.get(role, ""),
        "",
        "Return only JSON.",
        "Expected schema: [{\"title\": str, \"hypothesis\": str, \"dataset\": str, \"approach\": str, \"expected_signal\": str, \"risk\": str, \"priority\": int, \"controls\": [str], \"knob_assignments\": {str: str}}]",
        f"Generate at most {max_ideas} ideas.",
        "Prioritize ideas that could cause real latent-space improvement or transformer-level rewiring, not just format compliance.",
        "",
        f"Mission: {mission}",
        "",
        "Grounding findings that must constrain proposals:",
    ]
    for item in grounding.get("prior_findings", []):
        lines.append(f"- {item.get('id')}: {item.get('lesson')}")
    lines.extend(["", "Required evaluation controls:"])
    for item in grounding.get("evaluation_requirements", []):
        lines.append(f"- {item}")
    lines.extend(["", "Reusable knob families to vary dynamically instead of hardcoding per run:"])
    for item in knob_families[:10]:
        values = ", ".join(str(value) for value in item.get("candidate_values", []))
        lines.append(f"- {item.get('id')}: {item.get('description')} Values: {values}")
    lines.extend(["", "Research findings:"])
    for item in top_research:
        lines.append(f"- {item.get('title')} | published={item.get('published')} | score={item.get('relevance_score')}")
    lines.append("")
    lines.append("Candidate datasets and repos:")
    for item in top_datasets:
        lines.append(f"- {item.get('name')} | source={item.get('source')} | url={item.get('url') or item.get('path')}")
    return "\n".join(lines)


def heuristic_ideas(config: JSONObject, research: list[JSONObject], datasets: list[CatalogItem]) -> list[JSONObject]:
    templates = config["idea_generation"]["strategy_templates"]
    top_datasets = datasets[: max(1, min(len(datasets), 6))]
    top_papers = research[: max(1, min(len(research), 6))]
    controls = config["grounding"]["evaluation_requirements"]
    knob_families = config["recurrent_knobs"]["families"]
    ideas: list[JSONObject] = []
    for index, template in enumerate(templates, start=1):
        dataset = top_datasets[(index - 1) % len(top_datasets)] if top_datasets else {"name": "manual_dataset_slot"}
        paper = top_papers[(index - 1) % len(top_papers)] if top_papers else {"title": "recent recurrent-depth literature"}
        chosen_knobs = {
            family["id"]: str(family.get("candidate_values", ["default"])[(index - 1) % len(family.get("candidate_values", ["default"]))])
            for family in knob_families[:4]
        }
        ideas.append(
            {
                "title": template["title"],
                "hypothesis": template["hypothesis_template"].format(dataset=dataset.get("name"), paper=paper.get("title")),
                "dataset": dataset.get("name"),
                "approach": template["approach"],
                "expected_signal": template["expected_signal"],
                "risk": template["risk"],
                "priority": index,
                "source_mode": "heuristic",
                "controls": controls[:],
                "knob_assignments": chosen_knobs,
            }
        )
    return ideas


def generate_ideas(config: JSONObject, research: list[JSONObject], datasets: list[CatalogItem], prompts_dir: Path) -> list[JSONObject]:
    mission = config["mission"]["primary_question"]
    llm_config = config["idea_generation"]["llm"]
    roles = config["idea_generation"].get("roles", ["theorist", "data_scout", "skeptic"])
    max_ideas = int(config["idea_generation"].get("max_ideas", 6))
    adapter = build_adapter(llm_config)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    grounding = config["grounding"]
    knob_families = config["recurrent_knobs"]["families"]

    generated: list[JSONObject] = []
    for role in roles:
        prompt = build_prompt(
            role=role,
            mission=mission,
            research=research,
            datasets=datasets,
            grounding=grounding,
            knob_families=knob_families,
            max_ideas=max_ideas,
        )
        (prompts_dir / f"{role}.md").write_text(prompt)
        result = adapter.complete(prompt)
        ideas = parse_json_block(result.text)
        for item in ideas:
            item["source_mode"] = llm_config.get("provider", "none")
            item["role"] = role
            item.setdefault("controls", grounding.get("evaluation_requirements", []))
            item.setdefault("knob_assignments", {})
        generated.extend(ideas)

    if not generated:
        generated = heuristic_ideas(config, research=research, datasets=datasets)

    generated_with_order = list(enumerate(generated))
    deduped = dedupe_by_preference(
        generated_with_order,
        key_fn=lambda pair: str(pair[1].get("title", "")).strip().lower() or None,
        score_fn=lambda pair: -pair[0],
    )
    ranked = sorted((item for _, item in deduped), key=lambda item: item.get("priority", 999))
    return ranked[:max_ideas]


def save_ideas(ideas: list[JSONObject], path: Path) -> None:
    save_timestamped_json(path, "ideas", ideas)
