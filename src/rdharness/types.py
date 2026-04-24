from __future__ import annotations

from typing import TypeAlias, TypedDict, Union


JSONPrimitive: TypeAlias = None | bool | int | float | str
JSONValue: TypeAlias = Union[JSONPrimitive, "JSONObject", "JSONArray"]
JSONObject: TypeAlias = dict[str, JSONValue]
JSONArray: TypeAlias = list[JSONValue]


class CatalogItem(TypedDict, total=False):
    kind: str
    name: str
    path: str
    url: str
    notes: str
    source: str
    updated_at: str
    likes: int | float
    downloads: int | float
    query: str
    stars: int | float
    description: str


class GitHubSearchResults(TypedDict, total=False):
    items: list[JSONObject]


class LLMConfig(TypedDict, total=False):
    provider: str
    model: str
    base_url: str


class RecipeConfig(TypedDict, total=False):
    mode: str
    max_items: int
    marker: str


class RecipeManifest(TypedDict, total=False):
    recipes: dict[str, RecipeConfig]


class MaterializedVariantStats(TypedDict):
    recipe: str
    source_path: str
    output_path: str
    records_in: int
    records_out: int
    dataset_path: str


class RunSummary(TypedDict):
    title: JSONValue
    dataset: JSONValue
    command: str
    executed: bool
    returncode: int | None
    metrics: JSONObject
    score: float
    run_dir: str


class CycleReport(TypedDict):
    generated_at: str
    cycle: int
    research_count: int
    dataset_count: int
    idea_count: int
    runs: list[RunSummary]
    best_run: RunSummary | None


class WorkspaceState(TypedDict):
    workspace_version: int
    status: str
    active_cycle: int
    best_run: RunSummary | None


def default_workspace_state(status: str = "unknown") -> WorkspaceState:
    return {
        "workspace_version": 1,
        "status": status,
        "active_cycle": 0,
        "best_run": None,
    }
