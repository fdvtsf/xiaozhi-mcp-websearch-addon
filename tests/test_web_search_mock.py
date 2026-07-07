import pytest

from app.config import Settings
from app.web_search import ToolError, search_web


@pytest.mark.asyncio
async def test_web_search_rejects_empty_query():
    settings = Settings(search_provider="mock")
    with pytest.raises(ToolError):
        await search_web("", 3, "zh-CN", settings)


@pytest.mark.asyncio
async def test_mock_provider_returns_results():
    settings = Settings(search_provider="mock", max_search_results=5)
    payload = await search_web("Home Assistant MCP Server", 3, "zh-CN", settings)
    assert payload["provider"] == "mock"
    assert len(payload["results"]) == 3
    assert payload["results"][0]["url"].startswith("https://example.com/")


def test_default_provider_is_mock_for_development():
    assert Settings().search_provider == "mock"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider", ["bocha", "baidu_qianfan"])
async def test_china_providers_require_api_keys(provider):
    settings = Settings(search_provider=provider)
    with pytest.raises(ToolError):
        await search_web("Home Assistant MCP Server", 3, "zh-CN", settings)
