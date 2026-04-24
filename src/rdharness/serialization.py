from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

from .types import JSONObject


ItemT = TypeVar("ItemT")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_timestamped_json(path: Path, payload_key: str, items: Iterable[Any]) -> None:
    serialized_items = [serialize_item(item) for item in items]
    payload = {"generated_at": utc_now_iso(), payload_key: serialized_items}
    save_json(path, payload)


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2))


def load_json_list(path: Path, payload_key: str) -> list[JSONObject]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    items = data.get(payload_key, [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def dedupe_by_preference(
    items: Iterable[ItemT],
    *,
    key_fn: Callable[[ItemT], object | None],
    score_fn: Callable[[ItemT], Any],
) -> list[ItemT]:
    deduped: dict[str, ItemT] = {}
    for item in items:
        key = key_fn(item)
        if key is None:
            continue
        normalized_key = str(key)
        existing = deduped.get(normalized_key)
        if existing is None or score_fn(item) > score_fn(existing):
            deduped[normalized_key] = item
    return list(deduped.values())


def serialize_item(item: Any) -> Any:
    if is_dataclass(item):
        return asdict(item)
    return item
