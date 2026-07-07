# Xiaozhi MCP WebSearch

`Xiaozhi MCP WebSearch` is a Home Assistant add-on that exposes two web tools for a future Xiaozhi / Jarvis Gateway:

- `web_search`
- `fetch_url`

Current first version only implements联网搜索工具，不控制 Home Assistant 设备。Home Assistant 设备控制请继续使用 `xiaozhi-mcp-ha` 或官方 Home Assistant MCP Server。后续版本再考虑把 HA 控制和 WebSearch 合并成统一 MCP Gateway。

## Supported interface

v0.1.0 supports an HTTP tool API:

- `GET /health`
- `GET /tools`
- `POST /tools/web_search`
- `POST /tools/fetch_url`

`mode=xiaozhi_ws` actively connects to the Xiaozhi MCP access-point WebSocket URL and runs MCP JSON-RPC over that WebSocket, following `ha-mcp-for-xiaozhi`.

## Options

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

## Search providers

Recommended choices:

- Development default: `mock`
- China production default: `bocha`
- Low-cost backup: `baidu_qianfan`
- Optional compatibility providers: `searxng`, `brave`

Use Bocha:

```yaml
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
```

Use Baidu Qianfan Baidu Search:

```yaml
search_provider: baidu_qianfan
baidu_qianfan_api_key: "YOUR_APPBUILDER_API_KEY"
baidu_qianfan_edition: lite
```

Use SearxNG:

```yaml
search_provider: searxng
searxng_base_url: "https://your-searxng.example.com/"
```

Use Brave:

```yaml
search_provider: brave
brave_api_key: "YOUR_BRAVE_SEARCH_API_KEY"
```

Use mock for local testing:

```yaml
search_provider: mock
```

## Local API checks

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

## Safety

`safe_mode=true` blocks local/private network URLs, Home Assistant and Supervisor hostnames, metadata addresses, router hostnames, non-HTTP schemes, embedded credentials, oversized responses, and unsupported binary content types. Secrets are read from add-on options and redacted from logs.
## Xiaozhi WebSocket mode

```yaml
mode: xiaozhi_ws
xiaozhi_ws_endpoint: "wss://your-xiaozhi-mcp-access-point"
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
```

The add-on connects out to Xiaozhi. It does not provide an inbound Xiaozhi WebSocket URL.
