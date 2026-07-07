from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .fetch_url import fetch_url_text
from .models import Settings
from .web_search import ai_web_search, search_web


WEB_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query."},
        "count": {"type": "integer", "default": 5, "minimum": 1},
    },
    "required": ["query"],
}

AI_WEB_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Structured realtime search query."},
        "count": {"type": "integer", "default": 5, "minimum": 1},
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


async def call_tool(
    hass: HomeAssistant,
    name: str,
    payload: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    if name == "web_search":
        return await search_web(
            hass=hass,
            query=str(payload.get("query") or ""),
            count=payload.get("count"),
            language=payload.get("language"),
            settings=settings,
        )
    if name == "ai_web_search":
        return await ai_web_search(
            hass=hass,
            query=str(payload.get("query") or ""),
            count=payload.get("count"),
            settings=settings,
        )
    if name == "fetch_url":
        return await fetch_url_text(
            hass=hass,
            url=str(payload.get("url") or ""),
            max_chars=payload.get("max_chars"),
            settings=settings,
        )
    raise ValueError(f"unknown tool: {name}")
