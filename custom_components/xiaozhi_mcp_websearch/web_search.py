from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .models import Settings


_LOGGER = logging.getLogger(__name__)
BOCHA_AI_SEARCH_URL = "https://api.bocha.cn/v1/ai-search"


class ToolError(ValueError):
    pass


def _clean_result(item: dict[str, Any], provider: str) -> dict[str, Any]:
    return {
        "title": str(item.get("title") or "Untitled").strip(),
        "url": str(item.get("url") or "").strip(),
        "snippet": str(item.get("snippet") or item.get("content") or item.get("description") or "").strip(),
        "source": str(item.get("source") or provider).strip(),
        "raw": item.get("raw") or {},
    }


async def search_web(
    hass: HomeAssistant,
    query: str,
    count: int | None,
    language: str | None,
    settings: Settings,
) -> dict[str, Any]:
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
        results = await _bocha_web_search(hass, normalized_query, limit, settings)
    elif settings.search_provider == "baidu_qianfan":
        results = await _baidu_qianfan_search(hass, normalized_query, limit, settings)
    elif settings.search_provider == "searxng":
        results = await _searxng_search(hass, normalized_query, limit, lang, settings)
    elif settings.search_provider == "brave":
        results = await _brave_search(hass, normalized_query, limit, lang, settings)
    else:
        raise ToolError(f"unsupported search provider: {settings.search_provider}")

    return {
        "query": normalized_query,
        "tool": "web_search",
        "provider": settings.search_provider,
        "results": results[: settings.max_search_results],
    }


async def ai_web_search(hass: HomeAssistant, query: str, count: int | None, settings: Settings) -> dict[str, Any]:
    normalized_query = (query or "").strip()
    if not normalized_query:
        raise ToolError("query is required")
    if settings.search_provider != "bocha":
        raise ToolError("ai_web_search requires search_provider=bocha. Use web_search for this configuration.")
    if not _looks_like_ai_search_query(normalized_query):
        raise ToolError("ai_web_search is for structured realtime facts. Use web_search for normal web/news/tutorial searches.")

    limit = min(count or settings.max_search_results, settings.max_search_results)
    if limit < 1:
        raise ToolError("count must be at least 1")

    search_result = await _bocha_ai_search(hass, normalized_query, limit, settings)
    payload = {
        "query": normalized_query,
        "tool": "ai_web_search",
        "provider": "bocha",
        "results": search_result["results"][: settings.max_search_results],
    }
    if search_result.get("debug"):
        payload["debug"] = search_result["debug"]
    return payload


def _looks_like_ai_search_query(query: str) -> bool:
    lowered = query.lower()
    keywords = (
        "当前股价",
        "实时股价",
        "股票价格",
        "涨跌幅",
        "实时行情",
        "当前价格",
        "天气",
        "汇率",
        "油价",
        "百科",
        "参数",
        "配置",
        "stock price",
        "current price",
        "weather",
        "exchange rate",
    )
    if any(keyword in lowered for keyword in keywords):
        return True
    return any(code in lowered for code in ("01810.hk", "00700.hk", "nvda", "aapl", "tsla", "hk", ".hk"))


def _mock_results(query: str, limit: int) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "title": f"Mock result {index + 1} for {query}",
            "url": f"https://example.com/search/{index + 1}",
            "snippet": "This is a deterministic mock search result for local testing.",
            "source": "mock",
            "raw": {"published_at": timestamp},
        }
        for index in range(limit)
    ]


async def _bocha_web_search(
    hass: HomeAssistant,
    query: str,
    limit: int,
    settings: Settings,
) -> list[dict[str, Any]]:
    if not settings.bocha_api_key:
        raise ToolError("bocha_api_key is required when search_provider=bocha")

    headers = {
        "Authorization": f"Bearer {settings.bocha_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.2.0",
    }
    payload = {"query": query, "count": limit, "summary": True}
    data = await _post_json(hass, "web_search", settings.bocha_base_url, headers, payload, settings, query, limit)

    if str(data.get("code", "200")) not in {"0", "200"}:
        raise ToolError(str(data.get("msg") or data.get("message") or "bocha search failed"))

    raw_results = data.get("data", {}).get("webPages", {}).get("value", [])
    cleaned: list[dict[str, Any]] = []
    for item in raw_results[:limit]:
        result = _clean_result(
            {
                "title": item.get("name") or item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("summary") or item.get("snippet"),
                "source": item.get("siteName") or item.get("displayUrl") or "bocha",
                "raw": item,
            },
            "bocha",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _bocha_ai_search(
    hass: HomeAssistant,
    query: str,
    limit: int,
    settings: Settings,
) -> dict[str, Any]:
    if not settings.bocha_api_key:
        raise ToolError("bocha_api_key is required for ai_web_search")

    headers = {
        "Authorization": f"Bearer {settings.bocha_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.2.0",
    }
    payload = {
        "query": query,
        "freshness": "noLimit",
        "count": limit,
        "answer": False,
        "stream": False,
    }
    status, data = await _post_json_with_status(
        hass,
        "ai_web_search",
        BOCHA_AI_SEARCH_URL,
        headers,
        payload,
        settings,
        query,
        limit,
    )
    debug = {
        "endpoint": BOCHA_AI_SEARCH_URL,
        "count": limit,
        "http_status": status,
    }

    if status != 200:
        return {"results": [], "debug": debug}
    if data is None:
        return {"results": [], "debug": debug}

    if str(data.get("code", "200")) not in {"0", "200"}:
        debug["provider_message"] = str(data.get("msg") or data.get("message") or "bocha ai search failed")
        return {"results": [], "debug": debug}

    raw_results = _extract_bocha_result_items(data)
    if not raw_results:
        raw_results = _extract_bocha_message_fallback_items(data.get("messages", []))
    cleaned: list[dict[str, Any]] = []
    for item in raw_results[:limit]:
        normalized = _normalize_bocha_ai_item(item)
        result = _clean_result(
            {
                "title": normalized.get("title"),
                "url": normalized.get("url"),
                "snippet": normalized.get("snippet"),
                "source": normalized.get("source"),
                "raw": item,
            },
            "bocha",
        )
        cleaned.append(result)
    if cleaned:
        return {"results": cleaned}

    data_payload = data.get("data", {})
    if data_payload:
        return {
            "results": [
                {
                    "title": "Bocha AI Search structured result",
                    "url": "",
                    "snippet": "",
                    "source": "bocha",
                    "raw": data_payload,
                }
            ],
        }
    return {"results": [], "debug": debug}


def _normalize_bocha_ai_item(item: dict[str, Any]) -> dict[str, Any]:
    stock = _extract_stock_model_card(item)
    if stock:
        return stock
    return {
        "title": item.get("name") or item.get("title") or item.get("cardName") or item.get("type"),
        "url": item.get("url") or item.get("link") or item.get("displayUrl") or "",
        "snippet": item.get("summary") or item.get("snippet") or item.get("description") or item.get("content"),
        "source": item.get("siteName") or item.get("displayUrl") or item.get("source") or "bocha",
    }


def _extract_stock_model_card(item: dict[str, Any]) -> dict[str, Any] | None:
    groups = item.get("modelCard", {}).get("group")
    if not isinstance(groups, list) or not groups or not isinstance(groups[0], dict):
        return None

    stock = groups[0]
    title = stock.get("name") or item.get("name") or "Bocha stock quote"
    code = stock.get("code_stock")
    exchange = stock.get("name_exchange")
    fields = [
        ("price", stock.get("price")),
        ("time", stock.get("time")),
        ("status", stock.get("key_status")),
        ("open", stock.get("number_open")),
        ("high", stock.get("number_high")),
        ("low", stock.get("number_low")),
        ("previous_close", stock.get("number_closed")),
        ("market", stock.get("type")),
    ]
    snippet = ", ".join(f"{key}: {value}" for key, value in fields if value not in (None, ""))
    if code or exchange:
        title = f"{title} {code or ''}.{exchange or ''}".strip(".")

    return {
        "title": title,
        "url": item.get("url") or item.get("displayUrl") or "",
        "snippet": snippet,
        "source": item.get("siteName") or exchange or "bocha",
    }


def _extract_bocha_result_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    payload = data.get("data", {})
    candidates = [
        payload.get("webPages", {}).get("value"),
        payload.get("webpages", {}).get("value"),
        payload.get("results"),
        payload.get("cards"),
        payload.get("value"),
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    message_items = _extract_bocha_message_content_items(data.get("messages", []))
    if message_items:
        return message_items
    return []


def _extract_bocha_message_content_items(messages: Any) -> list[dict[str, Any]]:
    if not isinstance(messages, list):
        return []

    items: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        parsed = _parse_json_value(content)
        if parsed is None:
            continue
        items.extend(_extract_items_from_json_value(parsed))
    return items


def _extract_bocha_message_fallback_items(messages: Any) -> list[dict[str, Any]]:
    if not isinstance(messages, list):
        return []

    items: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        parsed = _parse_json_value(content)
        content_text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
        fallback = {
            "title": message.get("content_type") or message.get("type") or "Bocha AI Search result",
            "url": "",
            "summary": content_text[:1200],
            "source": "bocha",
            "content_type": message.get("content_type"),
            "raw": {
                "role": message.get("role"),
                "type": message.get("type"),
                "content_type": message.get("content_type"),
                "content": parsed if parsed is not None else content_text[:1200],
            },
        }
        items.append(fallback)
    return items


def _parse_json_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, str) and parsed != text:
        nested = _parse_json_value(parsed)
        if nested is not None:
            return nested
    return parsed if isinstance(parsed, (dict, list)) else None


def _extract_items_from_json_value(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        items: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                nested = _extract_items_from_json_value(item)
                items.extend(nested or [item])
        return items
    if not isinstance(value, dict):
        return []
    candidates = (
        value.get("value"),
        value.get("webPages", {}).get("value"),
        value.get("webpages", {}).get("value"),
        value.get("results"),
        value.get("cards"),
        value.get("data"),
    )
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, str):
            nested = _parse_json_value(candidate)
            nested_items = _extract_items_from_json_value(nested)
            if nested_items:
                return nested_items
        if isinstance(candidate, dict):
            nested_items = _extract_items_from_json_value(candidate)
            if nested_items:
                return nested_items
    return []


async def _baidu_qianfan_search(
    hass: HomeAssistant,
    query: str,
    limit: int,
    settings: Settings,
) -> list[dict[str, Any]]:
    if not settings.baidu_qianfan_api_key:
        raise ToolError("baidu_qianfan_api_key is required when search_provider=baidu_qianfan")

    headers = {
        "X-Appbuilder-Authorization": f"Bearer {settings.baidu_qianfan_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.2.0",
    }
    payload = {
        "messages": [{"role": "user", "content": query}],
        "edition": settings.baidu_qianfan_edition or "lite",
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": min(limit, 50)}],
        "safe_search": True,
    }

    data = await _post_json(
        hass,
        "web_search",
        settings.baidu_qianfan_base_url,
        headers,
        payload,
        settings,
        query,
        limit,
    )

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
                "raw": item,
            },
            "baidu_qianfan",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _searxng_search(
    hass: HomeAssistant,
    query: str,
    limit: int,
    language: str,
    settings: Settings,
) -> list[dict[str, Any]]:
    if not settings.searxng_base_url:
        raise ToolError("searxng_base_url is required when search_provider=searxng")

    endpoint = urljoin(settings.searxng_base_url.rstrip("/") + "/", "search")
    params = {"q": query, "format": "json", "language": language, "safesearch": 1}
    headers = {"User-Agent": "xiaozhi-mcp-websearch/0.2.0"}
    payload = await _get_json(hass, "web_search", endpoint, headers, params, settings, query, limit)

    cleaned: list[dict[str, Any]] = []
    for item in payload.get("results", [])[:limit]:
        result = _clean_result({**item, "raw": item}, "searxng")
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _brave_search(
    hass: HomeAssistant,
    query: str,
    limit: int,
    language: str,
    settings: Settings,
) -> list[dict[str, Any]]:
    if not settings.brave_api_key:
        raise ToolError("brave_api_key is required when search_provider=brave")

    headers = {
        "Accept": "application/json",
        "User-Agent": "xiaozhi-mcp-websearch/0.2.0",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {"q": query, "count": limit, "search_lang": language.split("-")[0]}
    payload = await _get_json(
        hass,
        "web_search",
        "https://api.search.brave.com/res/v1/web/search",
        headers,
        params,
        settings,
        query,
        limit,
    )

    cleaned: list[dict[str, Any]] = []
    for item in payload.get("web", {}).get("results", [])[:limit]:
        result = _clean_result(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
                "source": item.get("profile", {}).get("name") or "brave",
                "raw": item,
            },
            "brave",
        )
        if result["url"]:
            cleaned.append(result)
    return cleaned


async def _post_json(
    hass: HomeAssistant,
    tool_name: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    settings: Settings,
    query: str,
    count: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    session = async_get_clientsession(hass)
    timeout = ClientTimeout(total=settings.fetch_timeout_seconds)
    try:
        async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
            if response.status >= 400:
                raise ToolError(f"search provider returned HTTP {response.status}")
            data = await response.json(content_type=None)
    except asyncio.TimeoutError as exc:
        raise ToolError("search provider request timed out") from exc
    except ClientError as exc:
        raise ToolError("search provider request failed") from exc

    _log_search_call(tool_name, query, count, len(_extract_bocha_result_items(data)), started)
    return data


async def _post_json_with_status(
    hass: HomeAssistant,
    tool_name: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    settings: Settings,
    query: str,
    count: int,
) -> tuple[int, dict[str, Any] | None]:
    started = time.perf_counter()
    session = async_get_clientsession(hass)
    timeout = ClientTimeout(total=settings.fetch_timeout_seconds)
    status = 0
    body = ""
    try:
        async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
            status = response.status
            body = await response.text()
    except asyncio.TimeoutError as exc:
        raise ToolError("search provider request timed out") from exc
    except ClientError as exc:
        raise ToolError("search provider request failed") from exc

    data: dict[str, Any] | None = None
    if body:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            data = None

    result_count = len(_extract_bocha_result_items(data or {}))
    _LOGGER.debug(
        "MCP debug tool=%s endpoint=%s query=%r count=%s http_status=%s parsed_results=%s",
        tool_name,
        url,
        query[:80],
        count,
        status,
        result_count,
    )
    _log_search_call(tool_name, query, count, result_count, started)
    return status, data


async def _get_json(
    hass: HomeAssistant,
    tool_name: str,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
    settings: Settings,
    query: str,
    count: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    session = async_get_clientsession(hass)
    timeout = ClientTimeout(total=settings.fetch_timeout_seconds)
    try:
        async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
            if response.status >= 400:
                raise ToolError(f"search provider returned HTTP {response.status}")
            data = await response.json(content_type=None)
    except asyncio.TimeoutError as exc:
        raise ToolError("search provider request timed out") from exc
    except ClientError as exc:
        raise ToolError("search provider request failed") from exc

    result_count = len(data.get("results", [])) or len(data.get("web", {}).get("results", []))
    _log_search_call(tool_name, query, count, result_count, started)
    return data


def _log_search_call(tool_name: str, query: str, count: int, result_count: int, started: float) -> None:
    _LOGGER.info(
        "MCP tool=%s query=%r count=%s results=%s elapsed_ms=%s",
        tool_name,
        query[:80],
        count,
        result_count,
        int((time.perf_counter() - started) * 1000),
    )
