from __future__ import annotations

import json
from typing import Any

from homeassistant.core import HomeAssistant

from .const import VERSION
from .ha_tools import async_call_ha_tool, async_list_ha_tools
from .models import Settings
from .tools import AI_WEB_SEARCH_SCHEMA, FETCH_URL_SCHEMA, WEB_SEARCH_SCHEMA, call_tool

LOCAL_TOOL_NAMES = {"web_search", "ai_web_search", "fetch_url"}


def create_mcp_server(hass: HomeAssistant, settings: Settings):
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    import mcp.types as types

    server = Server("xiaozhi-mcp-websearch")

    @server.list_tools()
    async def list_mcp_tools() -> list[Any]:
        tools = [
            types.Tool(
                name="web_search",
                description=(
                    "低成本网页搜索工具。适合搜索新闻、网页、教程、公告、资料和原因分析。"
                    "不适合查询实时股价、天气、汇率、油价等结构化实时信息。"
                ),
                inputSchema=WEB_SEARCH_SCHEMA,
            ),
            types.Tool(
                name="fetch_url",
                description="Fetch and extract text from a public HTTP/HTTPS URL with safe-mode restrictions.",
                inputSchema=FETCH_URL_SCHEMA,
            ),
        ]
        if settings.search_provider == "bocha" and settings.bocha_api_key:
            tools.insert(
                1,
                types.Tool(
                    name="ai_web_search",
                    description=(
                        "高成本 AI 搜索工具。仅在用户明确询问实时股价、涨跌幅、天气、汇率、油价、百科卡、"
                        "手机/汽车参数等结构化信息时使用。不要用于普通新闻、教程、原因分析。"
                    ),
                    inputSchema=AI_WEB_SEARCH_SCHEMA,
                ),
            )
        tools.extend(await async_list_ha_tools(hass, settings, types.Tool))
        return tools

    @server.call_tool()
    async def call_mcp_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
        if name in LOCAL_TOOL_NAMES:
            payload = await call_tool(hass, name, arguments or {}, settings)
        else:
            payload = await async_call_ha_tool(hass, name, arguments or {}, settings)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(_json_safe(payload), ensure_ascii=False),
            )
        ]

    init_options = InitializationOptions(
        server_name="xiaozhi-mcp-websearch",
        server_version=VERSION,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    return server, init_options


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if hasattr(value, "as_dict"):
        return _json_safe(value.as_dict())
    return str(value)
