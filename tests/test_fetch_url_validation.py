import pytest

from app.config import Settings
from app.fetch_url import fetch_url_text
from app.web_search import ToolError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8123",
        "http://192.168.1.1",
    ],
)
async def test_fetch_url_blocks_private_addresses(url):
    settings = Settings(search_provider="mock", safe_mode=True)
    with pytest.raises(ToolError):
        await fetch_url_text(url, None, settings)


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["file:///etc/passwd", ""])
async def test_fetch_url_rejects_invalid_urls(url):
    settings = Settings(search_provider="mock", safe_mode=True)
    with pytest.raises(ValueError):
        await fetch_url_text(url, None, settings)

