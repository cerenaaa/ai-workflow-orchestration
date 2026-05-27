"""
Common LLM task implementations for workflow orchestration.
"""
from __future__ import annotations
import anthropic


_client = None
def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def summarize(text: str, max_words: int = 100) -> str:
    resp = get_client().messages.create(
        model="claude-sonnet-4-20250514", max_tokens=300,
        messages=[{"role": "user", "content": f"Summarize in {max_words} words:\n{text}"}]
    )
    return resp.content[0].text.strip()


def classify(text: str, categories: list = None) -> dict:
    cats = categories or ["positive", "negative", "neutral"]
    cats_str = ", ".join(cats)
    resp = get_client().messages.create(
        model="claude-sonnet-4-20250514", max_tokens=100,
        messages=[{"role": "user", "content": f"Classify into one of [{cats_str}]. Return JSON {{"category": "...", "confidence": 0.0}}. Text: {text}"}]
    )
    import json, re
    raw = re.sub(r"```(?:json)?\n?|\n?```", "", resp.content[0].text.strip())
    return json.loads(raw)


def translate(text: str, target_language: str = "Spanish") -> str:
    resp = get_client().messages.create(
        model="claude-sonnet-4-20250514", max_tokens=500,
        messages=[{"role": "user", "content": f"Translate to {target_language}. Return only the translation:\n{text}"}]
    )
    return resp.content[0].text.strip()


def extract_keywords(text: str, n: int = 5) -> list[str]:
    resp = get_client().messages.create(
        model="claude-sonnet-4-20250514", max_tokens=100,
        messages=[{"role": "user", "content": f"Extract {n} keywords. Return as JSON array of strings only. Text: {text}"}]
    )
    import json, re
    raw = re.sub(r"```(?:json)?\n?|\n?```", "", resp.content[0].text.strip())
    return json.loads(raw)
