# Future Gateway Plan

## Target architecture

```text
Xiaozhi device
-> Xiaozhi backend
-> Xiaozhi MCP Gateway
   |-- Home Assistant MCP Proxy
   |-- web_search
   |-- fetch_url
   |-- file_search
   |-- project_memory
   `-- pc_control
```

## Merge strategy

The future gateway should not mix all tool logic into one large protocol handler. It should keep protocol, routing, and tools separate:

- Protocol adapters: Xiaozhi WebSocket, standard MCP Streamable HTTP, MCP SSE, and possibly stdio.
- Tool registry: names, schemas, permissions, and routing.
- Tool providers: Home Assistant proxy, web search, URL fetch, file search, memory, and PC control.
- Security policy: per-tool allowlists, network restrictions, audit logs, and secret redaction.

## Home Assistant proxy

The HA control path should continue to use `xiaozhi-mcp-ha` or the official Home Assistant MCP Server until a gateway proxy is designed and tested. A later version can proxy HA MCP calls without this add-on directly reading or mutating HA entities.

## Xiaozhi protocol TODO

- Confirm whether Xiaozhi WebSocket authentication is always embedded in the access-point URL or can require extra headers.
- Confirm request and response message envelopes.
- Confirm streaming vs non-streaming responses.
- Confirm error format.
- Confirm whether multiple MCP endpoints are supported by the Xiaozhi backend.
- Confirm whether standard MCP transports are accepted.
