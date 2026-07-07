from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .models import Settings
from .security import is_url_allowed, validate_http_url
from .web_search import ToolError


ALLOWED_CONTENT_TYPES = {
    "text/html",
    "text/plain",
    "application/xhtml+xml",
    "application/xml",
    "text/xml",
}

BLOCKED_CONTENT_MARKERS = (
    "application/pdf",
    "image/",
    "video/",
    "audio/",
    "application/zip",
    "application/x-",
    "application/octet-stream",
)


async def fetch_url_text(hass: HomeAssistant, url: str, max_chars: int | None, settings: Settings) -> dict[str, Any]:
    current_url = validate_http_url(url)
    if not is_url_allowed(current_url, settings.safe_mode):
        raise ToolError("url is blocked by safe_mode")

    char_limit = min(max_chars or settings.max_fetch_chars, settings.max_fetch_chars)
    if char_limit < 1:
        raise ToolError("max_chars must be at least 1")

    headers = {"User-Agent": "xiaozhi-mcp-websearch/0.2.0"}
    session = async_get_clientsession(hass)
    response, final_url, raw = await _request_with_checked_redirects(
        session=session,
        url=current_url,
        safe_mode=settings.safe_mode,
        headers=headers,
        timeout_seconds=settings.fetch_timeout_seconds,
        max_bytes=max(char_limit * 4, 65536),
    )
    content_type = response.headers.get("content-type", "").split(";")[0].lower().strip()
    if not _is_supported_content_type(content_type):
        raise ToolError(f"unsupported content-type: {content_type or 'unknown'}")

    text, title = _extract_text(raw, content_type)
    truncated = len(text) > char_limit
    if truncated:
        text = text[:char_limit]

    return {
        "url": final_url,
        "title": title,
        "text": text,
        "content_type": content_type,
        "truncated": truncated,
    }


async def _request_with_checked_redirects(
    session: ClientSession,
    url: str,
    safe_mode: bool,
    headers: dict[str, str],
    timeout_seconds: int,
    max_bytes: int,
    max_redirects: int = 5,
) -> tuple[ClientResponse, str, bytes]:
    current = url
    for _ in range(max_redirects + 1):
        if not is_url_allowed(current, safe_mode):
            raise ToolError("redirect target is blocked by safe_mode")
        timeout = ClientTimeout(total=timeout_seconds)
        try:
            response = await session.get(current, headers=headers, timeout=timeout, allow_redirects=False)
        except asyncio.TimeoutError as exc:
            raise ToolError("fetch request timed out") from exc
        except ClientError as exc:
            raise ToolError("fetch request failed") from exc

        if response.status not in {301, 302, 303, 307, 308}:
            if response.status >= 400:
                response.release()
                raise ToolError(f"fetch returned HTTP {response.status}")
            raw = await _read_limited(response, max_bytes=max_bytes)
            return response, str(response.url), raw

        location = response.headers.get("location")
        response.release()
        if not location:
            raise ToolError("redirect response missing Location header")
        current = urljoin(current, location)

    raise ToolError("too many redirects")


async def _read_limited(response: ClientResponse, max_bytes: int) -> bytes:
    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > max_bytes:
        raise ToolError("response is too large")

    data = bytearray()
    async for chunk in response.content.iter_chunked(16384):
        data.extend(chunk)
        if len(data) > max_bytes:
            raise ToolError("response is too large")
    return bytes(data)


def _is_supported_content_type(content_type: str) -> bool:
    if not content_type:
        return True
    if content_type in ALLOWED_CONTENT_TYPES:
        return True
    return not any(content_type.startswith(marker) for marker in BLOCKED_CONTENT_MARKERS)


def _extract_text(raw: bytes, content_type: str) -> tuple[str, str]:
    content = raw.decode("utf-8", errors="replace")
    title = ""

    if content_type in {"text/html", "application/xhtml+xml"} or "<html" in content.lower():
        soup = BeautifulSoup(content, "html.parser")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = soup.get_text("\n")
    else:
        text = content

    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line), title
