from __future__ import annotations

import json
import shutil
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
import yaml

from .serialization import dedupe_by_preference, save_timestamped_json, utc_now_iso
from .types import CatalogItem, GitHubSearchResults


def discover_local_data(patterns: Iterable[str], root: Path) -> list[CatalogItem]:
    results: list[CatalogItem] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for match in root.glob(pattern):
            resolved = match.resolve()
            if resolved in seen or not resolved.is_file():
                continue
            seen.add(resolved)
            results.append(
                {
                    "kind": "local_file",
                    "name": resolved.name,
                    "path": str(resolved),
                    "source": "local",
                    "updated_at": datetime.fromtimestamp(resolved.stat().st_mtime, timezone.utc).isoformat(),
                }
            )
    return results


def discover_manual_sources(manifest_path: Path) -> list[CatalogItem]:
    if not manifest_path.exists():
        return []
    data = yaml.safe_load(manifest_path.read_text()) or {}
    items = data.get("sources", [])
    if not isinstance(items, list):
        return []
    normalized: list[CatalogItem] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "kind": item.get("kind", "manual"),
                "name": item.get("name", "unnamed-source"),
                "path": item.get("path"),
                "url": item.get("url"),
                "notes": item.get("notes", ""),
                "source": "manual_manifest",
                "updated_at": utc_now_iso(),
            }
        )
    return normalized


def discover_huggingface_datasets(queries: Iterable[str], limit: int = 5, timeout: int = 30) -> list[CatalogItem]:
    session = requests.Session()
    session.headers.update({"User-Agent": "rdharness/0.2"})
    results: list[CatalogItem] = []
    for query in queries:
        try:
            response = session.get(
                "https://huggingface.co/api/datasets",
                params={"search": query, "limit": limit},
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            warnings.warn(f"Hugging Face discovery failed for query {query!r}: {exc}", stacklevel=2)
            continue
        for item in payload:
            results.append(
                {
                    "kind": "dataset",
                    "name": item.get("id", "unknown"),
                    "url": f"https://huggingface.co/datasets/{item.get('id', '')}",
                    "likes": item.get("likes", 0),
                    "downloads": item.get("downloads", 0),
                    "query": query,
                    "source": "huggingface",
                    "updated_at": utc_now_iso(),
                }
            )
    return dedupe_catalog(results)


def discover_github_repos(queries: Iterable[str], limit: int = 5) -> list[CatalogItem]:
    results: list[CatalogItem] = []
    for query in queries:
        payload = _search_github_query(query=query, limit=limit)
        for item in payload.get("items", []):
            results.append(
                {
                    "kind": "repo",
                    "name": item.get("full_name", "unknown"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count", 0),
                    "description": item.get("description", ""),
                    "query": query,
                    "source": "github",
                    "updated_at": item.get("updated_at"),
                }
            )
    return dedupe_catalog(results)


def _search_github_query(query: str, limit: int) -> GitHubSearchResults:
    if shutil.which("gh") is not None:
        try:
            completed = subprocess.run(
                [
                    "gh",
                    "api",
                    "search/repositories",
                    "-f",
                    f"q={query}",
                    "-f",
                    f"per_page={limit}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(completed.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            warnings.warn(f"GitHub CLI search failed for query {query!r}; falling back to HTTP: {exc}", stacklevel=2)

    try:
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "per_page": limit},
            headers={"Accept": "application/vnd.github+json", "User-Agent": "rdharness/0.2"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        warnings.warn(f"GitHub HTTP search failed for query {query!r}: {exc}", stacklevel=2)
        return {"items": []}


def dedupe_catalog(items: list[CatalogItem]) -> list[CatalogItem]:
    deduped = dedupe_by_preference(
        items,
        key_fn=lambda item: item.get("url") or item.get("path") or item.get("name"),
        score_fn=score_catalog_item,
    )
    return sorted(deduped, key=score_catalog_item, reverse=True)


def score_catalog_item(item: CatalogItem) -> float:
    score = 0.0
    for key in ("likes", "downloads", "stars"):
        value = item.get(key, 0) or 0
        try:
            score += min(float(value), 5000.0) / 100.0
        except (TypeError, ValueError):
            continue
    name = str(item.get("name", "")).lower()
    query = str(item.get("query", "")).lower()
    score += sum(1.0 for token in query.split() if len(token) > 3 and token in name)
    return round(score, 3)


def save_catalog(items: list[CatalogItem], path: Path) -> None:
    save_timestamped_json(path, "items", items)
