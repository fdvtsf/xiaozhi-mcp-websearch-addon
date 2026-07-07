# Protocol Design

## v0.1.0 supported interface

The first release exposes an HTTP tool API:

- `GET /health`
- `GET /tools`
- `POST /tools/web_search`
- `POST /tools/fetch_url`

This is MCP-like, but it is not claimed to be a complete standard MCP transport.

## Tool discovery

`GET /tools` returns:

```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "...",
      "input_schema": {}
    },
    {
      "name": "fetch_url",
      "description": "...",
      "input_schema": {}
    }
  ]
}
```

## Tool calls

`POST /tools/web_search` accepts:

```json
{
  "query": "Home Assistant MCP Server",
  "count": 3,
  "language": "zh-CN"
}
```

`POST /tools/fetch_url` accepts:

```json
{
  "url": "https://www.home-assistant.io/",
  "max_chars": 12000
}
```

## Xiaozhi WebSocket mode

`mode=mcp_http` is the default local test mode.

`mode=mcp_sse` and `/sse` are reserved for a later standard MCP SSE transport.

`/mcp` is reserved for standard MCP Streamable HTTP.

`mode=xiaozhi_ws` follows the transport pattern used by `c1pher-cn/ha-mcp-for-xiaozhi`: the add-on actively connects to the Xiaozhi MCP access-point WebSocket URL and runs an MCP Server over that WebSocket stream.

Important distinction:

- `xiaozhi_ws_endpoint` is the WebSocket URL provided by Xiaozhi backend configuration.
- `/xiaozhi/ws` is not an inbound endpoint in this add-on.
- HTTP `/tools/*` endpoints remain available only in `mcp_http` mode for local testing and integrations that can call simple HTTP tools.

The WebSocket payload is standard MCP JSON-RPC. The adapter converts WebSocket text frames into MCP `SessionMessage` objects and sends MCP server responses back as WebSocket text frames.

The transport also sends a ping heartbeat, defaulting to 50 seconds, matching the reference implementation's behavior.

## Future adapter shape

The code keeps tool logic behind `app.tools.call_tool()`. A later protocol adapter should:

1. Keep `xiaozhi_ws` as the outbound transport for Xiaozhi.
2. Add inbound standard MCP Streamable HTTP or SSE only if another client needs it.
3. Keep tool execution behind `call_tool()` so every transport shares the same implementation.

## Current Xiaozhi limitation

If the Xiaozhi backend only supports one MCP endpoint today, this add-on should not be forcibly merged with `xiaozhi-mcp-ha` in v0.1.0. Run this add-on as a separate web-search capability where multiple endpoints are supported, or wait for the future gateway adapter.
