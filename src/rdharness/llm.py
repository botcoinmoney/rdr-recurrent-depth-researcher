from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests

from .types import JSONObject, LLMConfig


@dataclass
class LLMResult:
    text: str
    raw: JSONObject


class BaseAdapter:
    def complete(self, prompt: str) -> LLMResult:
        raise NotImplementedError


class NoopAdapter(BaseAdapter):
    def complete(self, prompt: str) -> LLMResult:
        return LLMResult(text="", raw={"mode": "noop", "prompt": prompt})


class OpenAIResponsesAdapter(BaseAdapter):
    def __init__(self, model: str, api_key: str, base_url: str | None = None, timeout: int = 90) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.timeout = timeout

    def complete(self, prompt: str) -> LLMResult:
        response = requests.post(
            f"{self.base_url}/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": prompt,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        text_parts: list[str] = []
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text_parts.append(content.get("text", ""))
        return LLMResult(text="\n".join(part for part in text_parts if part).strip(), raw=payload)


class AnthropicAdapter(BaseAdapter):
    def __init__(self, model: str, api_key: str, timeout: int = 90) -> None:
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, prompt: str) -> LLMResult:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        text = "\n".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
        return LLMResult(text=text.strip(), raw=payload)


def build_adapter(llm_config: LLMConfig) -> BaseAdapter:
    provider = llm_config.get("provider", "none")
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return NoopAdapter()
        return OpenAIResponsesAdapter(
            model=llm_config.get("model", "gpt-5.4"),
            api_key=api_key,
            base_url=llm_config.get("base_url"),
        )
    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return NoopAdapter()
        return AnthropicAdapter(
            model=llm_config.get("model", "claude-sonnet-4-5"),
            api_key=api_key,
        )
    return NoopAdapter()


def parse_json_block(text: str) -> list[JSONObject]:
    if not text:
        return []
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if "\n" in stripped:
            stripped = stripped.split("\n", 1)[1]
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]
