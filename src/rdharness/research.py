from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from xml.etree import ElementTree

import requests

from .serialization import dedupe_by_preference, load_json_list, save_timestamped_json
from .types import JSONObject


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class ResearchPaper:
    title: str
    summary: str
    url: str
    published: str
    updated: str
    authors: list[str]
    query: str
    relevance_score: float


def _parse_entry(entry: ElementTree.Element, query: str) -> ResearchPaper:
    title = (entry.findtext("atom:title", default="", namespaces=ATOM_NS) or "").strip()
    summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ATOM_NS) or "").split())
    url = entry.findtext("atom:id", default="", namespaces=ATOM_NS) or ""
    published = entry.findtext("atom:published", default="", namespaces=ATOM_NS) or ""
    updated = entry.findtext("atom:updated", default="", namespaces=ATOM_NS) or ""
    authors = [
        (author.findtext("atom:name", default="", namespaces=ATOM_NS) or "").strip()
        for author in entry.findall("atom:author", namespaces=ATOM_NS)
    ]
    relevance_score = score_paper(title=title, summary=summary, published=published, query=query)
    return ResearchPaper(
        title=title,
        summary=summary,
        url=url,
        published=published,
        updated=updated,
        authors=authors,
        query=query,
        relevance_score=relevance_score,
    )


def score_paper(title: str, summary: str, published: str, query: str) -> float:
    now = datetime.now(timezone.utc)
    query_terms = {term.lower() for term in query.replace("-", " ").split() if len(term) > 3}
    haystack = f"{title} {summary}".lower()
    overlap = sum(1 for term in query_terms if term in haystack)
    try:
        published_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        age_days = max((now - published_dt).days, 0)
    except ValueError:
        age_days = 365
    recency_bonus = max(0.0, 2.0 - (age_days / 365.0))
    return round(overlap + recency_bonus, 3)


def fetch_arxiv_papers(queries: Iterable[str], max_results: int = 8, timeout: int = 30) -> list[ResearchPaper]:
    papers: list[ResearchPaper] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "rdharness/0.2"})

    for query in queries:
        params = urlencode(
            {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
        response = session.get(f"{ARXIV_API_URL}?{params}", timeout=timeout)
        response.raise_for_status()
        feed = ElementTree.fromstring(response.text)
        papers.extend(_parse_entry(entry, query=query) for entry in feed.findall("atom:entry", namespaces=ATOM_NS))

    deduped = dedupe_by_preference(
        papers,
        key_fn=lambda paper: paper.url,
        score_fn=lambda paper: paper.relevance_score,
    )
    return sorted(deduped, key=lambda item: (item.relevance_score, item.published), reverse=True)


def save_research_snapshot(papers: list[ResearchPaper], output_path: Path) -> None:
    save_timestamped_json(output_path, "papers", papers)


def load_research_snapshot(path: Path) -> list[JSONObject]:
    return load_json_list(path, "papers")
