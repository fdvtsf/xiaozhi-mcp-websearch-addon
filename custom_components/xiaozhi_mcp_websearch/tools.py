from __future__ import annotations

from typing import Any

from .fetch_url import fetch_url_text
from .models import Settings
from .web_search import search_web


WEB_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query."},
        "count": {"type": "integer", "default": 5, "minimum": 1},
        "language": {"type": "string", "default": "zh-CN"},
    },
    "required": ["query"],
}

FETCH_URL_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "HTTP or HTTPS URL to fetch."},
        "max_chars": {"type": "integer", "minimum": 1},
    },
    "required": ["url"],
}


async def call_tool(name: str, payload: dict[str, Any], settings: Settings) -> dict[str, Any]:
    if name == "web_search":
        return await search_web(
            query=str(payload.get("query") or ""),
            count=payload.get("count"),
            language=payload.get("language"),
            settings=settings,
        )
    if name == "fetch_url":
        return await fetch_url_text(
            url=str(payload.get("url") or ""),
            max_chars=payload.get("max_chars"),
            settings=settings,
        )
    raise ValueError(f"unknown tool: {name}")

