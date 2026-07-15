# Xiaozhi MCP WebSearch

Home Assistant WebSearch MCP tools for Xiaozhi / Jarvis Gateway.

This repository now provides two install shapes:

- **Recommended for low disk space:** Home Assistant custom integration in `custom_components/xiaozhi_mcp_websearch`
- **Optional legacy shape:** Home Assistant Add-on in `xiaozhi_mcp_websearch`

The custom integration does not use Docker build and is closer to `ha-mcp-for-xiaozhi`.

Current custom integration implements web search tools and can optionally expose Home Assistant Assist/LLM tools through the same Xiaozhi MCP WebSocket connection. Home Assistant tools are disabled by default and must be explicitly enabled in the integration options.

The Home Assistant tool bridge follows the same direction as `ha-mcp-for-xiaozhi`: it reuses Home Assistant's official Assist/LLM API instead of reimplementing entity and service-control logic.

## Current capabilities

- `web_search`
  - mock provider for default development testing
  - Bocha provider for default China production deployments
  - Baidu Qianfan Baidu Search provider as a low-cost backup
  - SearxNG provider
  - Brave Search API provider
- `fetch_url`
  - HTTP/HTTPS only
  - text extraction only
  - private network blocking in safe mode
- HTTP tool API:
  - `GET /health`
  - `GET /tools`
  - `POST /tools/web_search`
  - `POST /tools/fetch_url`
- Xiaozhi WebSocket MCP mode:
  - outbound connection to the Xiaozhi MCP access-point URL
  - MCP JSON-RPC over WebSocket, following `ha-mcp-for-xiaozhi`
- Optional Home Assistant Assist/LLM tools:
  - disabled by default
  - dynamically exposed from Home Assistant's official Assist/LLM API
  - intended to provide the HA-control side of a unified Xiaozhi MCP Gateway

## Home Assistant Tools

To expose Home Assistant device/control tools to Xiaozhi:

1. Open **Settings > Devices & services > Xiaozhi MCP WebSearch > Configure**.
2. Enable **Home Assistant tools**.
3. Keep `ha_llm_api` as `assist` unless your HA instance uses another LLM API id.
4. Keep `ha_assistant` as `conversation` unless your exposed entities are scoped to another assistant id.
5. Restart the integration or Home Assistant Core.

When enabled, the integration dynamically lists tools from Home Assistant's official Assist/LLM API and adds them next to `web_search` and `fetch_url`.

## Not supported in v0.3.1

- Bocha AI Search and the former `ai_web_search` tool
- Supervisor API access
- Inbound standard MCP Streamable HTTP or SSE transport
- Binary document download, PDF extraction, image/video/archive extraction

## Repository layout

```text
xiaozhi-mcp-websearch-addon/
├── repository.json
├── README.md
├── custom_components/
│   └── xiaozhi_mcp_websearch/
├── xiaozhi_mcp_websearch/
│   ├── config.yaml
│   ├── Dockerfile
│   ├── run.sh
│   ├── requirements.txt
│   ├── README.md
│   └── app/
├── tests/
└── docs/
```

## Recommended: custom integration installation

If HAOS has limited free disk space, use the custom integration version:

1. Copy `custom_components/xiaozhi_mcp_websearch` to `/config/custom_components/xiaozhi_mcp_websearch`.
2. Restart Home Assistant Core.
3. Open **Settings > Devices & services > Add integration**.
4. Search **Xiaozhi MCP WebSearch**.
5. Fill the Xiaozhi MCP WebSocket endpoint and search provider settings.

Chinese guide: [docs/custom-component-install-cn.md](docs/custom-component-install-cn.md)

## Home Assistant installation

The Add-on version is still available, but it needs Docker build space and Docker Hub access.

1. Publish or copy this folder as a Home Assistant add-on repository.
2. In Home Assistant, open **Settings > Add-ons > Add-on Store**.
3. Open **Repositories** and add this repository URL.
4. Install **Xiaozhi MCP WebSearch**.
5. Start with `search_provider: mock` to verify the service.

Chinese step-by-step guide: [docs/haos-install-cn.md](docs/haos-install-cn.md)

Raspberry Pi 4B with 64-bit HAOS uses `aarch64`; this add-on also supports `amd64`.

## Configuration

```yaml
mode: mcp_http
host: 0.0.0.0
port: 8765
public_base_url: ""
xiaozhi_ws_endpoint: ""
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: mock
bocha_api_key: ""
bocha_base_url: "https://api.bochaai.com/v1/web-search"
baidu_qianfan_api_key: ""
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
searxng_base_url: ""
brave_api_key: ""
max_search_results: 5
fetch_timeout_seconds: 10
max_fetch_chars: 12000
safe_mode: true
log_level: info
```

`mode=mcp_http` is the default local test mode. `mode=xiaozhi_ws` actively connects to the Xiaozhi MCP access-point WebSocket URL. `mode=mcp_sse` is still reserved.

## Xiaozhi WebSocket MCP mode

This mode follows the transport used by [`c1pher-cn/ha-mcp-for-xiaozhi`](https://github.com/c1pher-cn/ha-mcp-for-xiaozhi): the add-on connects out to the Xiaozhi MCP access-point WebSocket URL, and the WebSocket carries standard MCP JSON-RPC messages.

```yaml
mode: xiaozhi_ws
xiaozhi_ws_endpoint: "wss://your-xiaozhi-mcp-access-point"
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
```

`xiaozhi_ws_endpoint` may contain credentials in the URL, so it is treated as a password in add-on configuration and redacted from logs.

## Recommended provider choices

- Development default: `mock`
- China production default: `bocha`
- Low-cost backup: `baidu_qianfan`
- Optional compatibility providers: `searxng`, `brave`

## Bocha example

```yaml
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
bocha_base_url: "https://api.bochaai.com/v1/web-search"
```

## Baidu Qianfan Baidu Search example

```yaml
search_provider: baidu_qianfan
baidu_qianfan_api_key: "YOUR_APPBUILDER_API_KEY"
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
```

`lite` is the recommended low-cost backup edition. Use the AppBuilder API Key for the `X-Appbuilder-Authorization` bearer token.

## SearxNG example

```yaml
search_provider: searxng
searxng_base_url: "https://your-searxng.example.com/"
```

## Brave Search API example

```yaml
search_provider: brave
brave_api_key: "YOUR_BRAVE_SEARCH_API_KEY"
```

Keys are read from add-on configuration and redacted from logs.

## Mock provider test

```yaml
search_provider: mock
```

Then:

```bash
curl -X POST http://localhost:8765/tools/web_search \
  -H "Content-Type: application/json" \
  -d '{"query":"Home Assistant MCP Server","count":3}'
```

## API test commands

```bash
curl http://localhost:8765/health
curl http://localhost:8765/tools
curl -X POST http://localhost:8765/tools/web_search \
  -H "Content-Type: application/json" \
  -d '{"query":"Home Assistant MCP Server","count":3}'
curl -X POST http://localhost:8765/tools/fetch_url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.home-assistant.io/"}'
```

## Local development

```bash
cd xiaozhi-mcp-websearch-addon/xiaozhi_mcp_websearch
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

or:

```bash
python -m app.main
```

Run tests:

```bash
cd xiaozhi-mcp-websearch-addon/xiaozhi_mcp_websearch
python -m pip install -r requirements.txt
python -m pip install -r ../requirements-dev.txt
PYTHONPATH=. pytest ../tests
```

## Security notes

`fetch_url` safe mode rejects private IPs, local hostnames, Home Assistant/Supervisor hostnames, metadata IPs, router hostnames, non-HTTP schemes, embedded credentials, large responses, and binary content types. Redirect targets are checked before they are requested.

## Relationship with `xiaozhi-mcp-ha`

Run both components in parallel:

```text
Xiaozhi device -> Xiaozhi backend -> xiaozhi-mcp-ha -> HA MCP Server -> devices
Xiaozhi device -> Xiaozhi backend -> Xiaozhi MCP WebSearch -> web_search / fetch_url
```

If the Xiaozhi side currently only allows one MCP endpoint, run either `xiaozhi-mcp-ha` or this WebSearch add-on for that access point, or wait for the future unified gateway.

## Roadmap

- Add optional extra headers for Xiaozhi WebSocket authentication if needed.
- Add standard MCP Streamable HTTP or SSE transport.
- Add optional authentication for the HTTP tool API.
- Merge with a Home Assistant MCP proxy in a future Xiaozhi MCP Gateway.
