# Research Notes

## Short conclusion

Current v0.1.0 can implement a Home Assistant add-on that exposes stable HTTP tool endpoints:

- `GET /health`
- `GET /tools`
- `POST /tools/web_search`
- `POST /tools/fetch_url`

The add-on is suitable to run alongside `xiaozhi-mcp-ha`. It does not read Home Assistant entities, does not call HA APIs, and does not control devices.

Search provider decision after the second API update:

- Development default: `mock`.
- China production default: `bocha`, using Bocha Web Search.
- Low-cost backup: `baidu_qianfan`, using Baidu Qianfan Baidu Search.
- `searxng` and `brave` remain optional compatibility providers.

Protocol details now confirmed from `c1pher-cn/ha-mcp-for-xiaozhi`:

- The Xiaozhi side provides an MCP access-point WebSocket URL.
- The server component actively connects out to that URL.
- The WebSocket carries standard MCP JSON-RPC messages.
- The Python implementation can use the MCP SDK `Server.run(read_stream, write_stream, options)` pattern.

Protocol details still needing confirmation:

- Whether the access-point URL embeds all authentication in the URL or can require extra headers.
- Whether the Xiaozhi backend can configure multiple MCP endpoints at once.

Places that must match Xiaozhi backend configuration later:

- Public or LAN URL for this add-on, for example `http://<ha-ip>:8765`.
- Xiaozhi MCP access-point WebSocket URL when `mode=xiaozhi_ws`.
- HTTP tool endpoint path only when using `mode=mcp_http`.
- Any Xiaozhi-specific authentication or WebSocket handshake fields.

## Home Assistant add-on structure

Home Assistant add-on repositories contain a repository metadata file and one directory per add-on. Each add-on directory normally includes:

- `config.yaml` for Supervisor metadata, schema, ports, architecture, startup behavior, and options.
- `Dockerfile` for building the add-on container image.
- `run.sh` or equivalent entrypoint script.

Reference:

- [Home Assistant add-on configuration](https://developers.home-assistant.io/docs/add-ons/configuration/)
- [Home Assistant add-on repository](https://developers.home-assistant.io/docs/add-ons/repository/)

## Basic `config.yaml`, `Dockerfile`, and `run.sh`

The v0.1.0 add-on uses:

- `arch: [aarch64, amd64]`
- `startup: services`
- `boot: auto`
- `init: false`
- `host_network: false`
- `/data/options.json` as the Supervisor-provided options file.

The Dockerfile uses a multi-architecture `python:3.12-slim` base by default. The add-on process runs as a non-root `appuser` after dependencies and files are installed.

## Raspberry Pi 4B / HAOS architecture

Raspberry Pi 4B with a 64-bit Home Assistant OS image corresponds to `aarch64`. This add-on also includes `amd64` for local development and x86 HAOS installations.

Reference:

- [Home Assistant installation docs](https://www.home-assistant.io/installation/)

## MCP server basics

Model Context Protocol servers expose capabilities such as tools. In the standard protocol, clients discover tools and call them using MCP JSON-RPC methods such as `tools/list` and `tools/call`. Tool definitions include names, descriptions, and input schemas.

Reference:

- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/)
- [MCP tools concept](https://modelcontextprotocol.io/docs/concepts/tools)

## Xiaozhi MCP protocol status

The user-provided local `ws_mcp_server` path was not readable in the current sandbox, but the GitHub project `c1pher-cn/ha-mcp-for-xiaozhi` confirms the core transport: outbound WebSocket carrying MCP JSON-RPC.

Implementation decision:

- Default `mode=mcp_http`.
- `mode=mcp_sse` is reserved and returns a clear not-implemented response.
- `mode=xiaozhi_ws` actively connects to `xiaozhi_ws_endpoint`.
- The HTTP tool API is intentionally simple so it can become the backing implementation for a later MCP or Xiaozhi WebSocket adapter.
