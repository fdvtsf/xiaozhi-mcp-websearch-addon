from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import httpx

from .config import Settings


class ToolError(ValueError):
    pass


def _clean_result(item: dict[str, Any], provider: str) -> dict[str, str | None]:
    return {
        "title": str(item.get("title") or "Untitled").strip(),
        "url": str(item.get("url") or "").strip(),
        "snippet": str(item.get("snippet") or item.get("content") or item.get("description") or "").strip(),
        "source": str(item.get("source") or provider).strip(),
        "published_at": item.get("published_at") or item.get("published") or None,
    }


async def search_web(query: str, count: int | None, language: str | None, settings: Settings) -> dict[str, Any]:
    normalized_query = (query or "").strip()
    if not normalized_query:
        raise ToolError("query is required")

    limit = min(count or settings.max_search_results, settings.max_search_results)
    if limit < 1:
        raise ToolError("count must be at least 1")
    lang = (language or "zh-CN").strip() or "zh-CN"

    if settings.search_provider == "mock":
        results = _mock_results(normalized_query, limit)
    elif settings.search_provider == "bocha":
        results = await _bocha_search(normalized_query, limit, lang, settings)
    elif settings.search_provider == "baidu_qianfan":
        results = await _baidu_qianfan_search(normalized_query, limit, lang, settings)
    elif settings.search_provider == "searxng":
        results = await _searxng_search(normalized_query, limit, lang, settings)
    elif settings.search_provider == "brave":
        results = await _brave_search(normalized_query, limit, lang, settings)
    else:
        raise ToolError(f"unsupported search provider: {settings.search_provider}")

    return {
        "query": normalized_query,
        "provider": settings.search_provider,
        "results": results[: settings.max_search_results],
    }


def _mock_results(query: str, limit: int) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "title": f"Mock result {index + 1} for {query}",
            "url": f"https://example.com/search/{index + 1}",
            "snippet": "This is a deterministic mock search result for local add-on testing.",
            "source": "mock",
            "published_at": timestamp,
        }
        for index in range(limit)
    ]


async def _searxng_search(query: str, limit: int, language: str, settings: Settings) -> list[dict[str, Any]]:
    if not settings.searxng_base_url:
        raise ToolError("searxng_base_url is required when search_provider=searxng")

    endpoint = urljoin(settings.searxng_base_url.rstrip("/") + "/", "search")
    params = {
        "q": query,
        "format": "json",
        "language": language,
        "safesearch": 1,
    }
    headers = {"User-Agent": "xiaozhi-mcp-websearch/0.1.0"}

    async with httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, headers=headers) as client:
        response = await client.get(endpoint, params=params)
        response.raise_for_status()
        payload = response.json()

    raw_results = payload.get("results", [])
    cleaned: list[dict[str, Any]] = []
    for item in raw_results[:limit]:
        result = _clean_result(item, "searxng")
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _bocha_search(query: str, limit: int, language: str, settings: Settings) -> list[dict[str, Any]]:
    if not settings.bocha_api_key:
        raise ToolError("bocha_api_key is required when search_provider=bocha")
    if not settings.bocha_base_url:
        raise ToolError("bocha_base_url is required when search_provider=bocha")

    headers = {
        "Authorization": f"Bearer {settings.bocha_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.1.0",
    }
    payload = {
        "query": query,
        "count": limit,
        "summary": True,
    }

    async with httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, headers=headers) as client:
        response = await client.post(settings.bocha_base_url, json=payload)
        response.raise_for_status()
        data = response.json()

    if str(data.get("code", "200")) not in {"0", "200"}:
        raise ToolError(str(data.get("msg") or data.get("message") or "bocha search failed"))

    raw_results = (
        data.get("data", {})
        .get("webPages", {})
        .get("value", [])
    )
    cleaned: list[dict[str, Any]] = []
    for item in raw_results[:limit]:
        result = _clean_result(
            {
                "title": item.get("name") or item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("summary") or item.get("snippet"),
                "source": item.get("siteName") or item.get("displayUrl") or "bocha",
                "published_at": item.get("dateLastCrawled") or item.get("datePublished"),
            },
            "bocha",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _baidu_qianfan_search(query: str, limit: int, language: str, settings: Settings) -> list[dict[str, Any]]:
    if not settings.baidu_qianfan_api_key:
        raise ToolError("baidu_qianfan_api_key is required when search_provider=baidu_qianfan")
    if not settings.baidu_qianfan_base_url:
        raise ToolError("baidu_qianfan_base_url is required when search_provider=baidu_qianfan")

    headers = {
        "X-Appbuilder-Authorization": f"Bearer {settings.baidu_qianfan_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.1.0",
    }
    payload = {
        "messages": [{"role": "user", "content": query}],
        "edition": settings.baidu_qianfan_edition or "lite",
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": min(limit, 50)}],
        "safe_search": True,
    }

    async with httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, headers=headers) as client:
        response = await client.post(settings.baidu_qianfan_base_url, json=payload)
        response.raise_for_status()
        data = response.json()

    if data.get("code"):
        raise ToolError(str(data.get("message") or "baidu qianfan search failed"))

    cleaned: list[dict[str, Any]] = []
    for item in data.get("references", [])[:limit]:
        if item.get("type") and item.get("type") != "web":
            continue
        result = _clean_result(
            {
                "title": item.get("title") or item.get("web_anchor"),
                "url": item.get("url"),
                "snippet": item.get("snippet") or item.get("content"),
                "source": item.get("website") or item.get("web_anchor") or "baidu_qianfan",
                "published_at": item.get("date"),
            },
            "baidu_qianfan",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _brave_search(query: str, limit: int, language: str, settings: Settings) -> list[dict[str, Any]]:
    if not settings.brave_api_key:
        raise ToolError("brave_api_key is required when search_provider=brave")

    headers = {
        "Accept": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.1.0",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {
        "q": query,
        "count": limit,
        "search_lang": language.split("-")[0],
    }

    async with httpx.AsyncClient(timeout=settings.fetch_timeout_seconds, headers=headers) as client:
        response = await client.get("https://api.search.brave.com/res/v1/web/search", params=params)
        response.raise_for_status()
        payload = response.json()

    raw_results = payload.get("web", {}).get("results", [])
    cleaned: list[dict[str, Any]] = []
    for item in raw_results[:limit]:
        result = _clean_result(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
                "source": item.get("profile", {}).get("name") or "brave",
                "published_at": item.get("age"),
            },
            "brave",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned
