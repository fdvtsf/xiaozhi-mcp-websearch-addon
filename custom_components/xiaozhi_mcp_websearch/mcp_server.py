from __future__ import annotations

import json
from typing import Any

from .const import VERSION
from .models import Settings
from .tools import FETCH_URL_SCHEMA, WEB_SEARCH_SCHEMA, call_tool


def create_mcp_server(settings: Settings):
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    import mcp.types as types

    server = Server("xiaozhi-mcp-websearch")

    @server.list_tools()
    async def list_mcp_tools() -> list[Any]:
        return [
            types.Tool(
                name="web_search",
                description="Search the web using mock, Bocha, Baidu Qianfan Baidu Search, SearxNG, or Brave Search.",
                inputSchema=WEB_SEARCH_SCHEMA,
            ),
            types.Tool(
                name="fetch_url",
                description="Fetch and extract text from a public HTTP/HTTPS URL with safe-mode restrictions.",
                inputSchema=FETCH_URL_SCHEMA,
            ),
        ]

    @server.call_tool()
    async def call_mcp_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
        payload = await call_tool(name, arguments or {}, settings)
        return [
            types.TextContent(
                type="text",
                text=json.dumps(payload, ensure_ascii=False),
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

