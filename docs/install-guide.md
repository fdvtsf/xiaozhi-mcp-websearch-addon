# Install Guide

## Add the repository in Home Assistant

1. Copy or publish this folder as a Home Assistant add-on repository.
2. In Home Assistant, open **Settings > Add-ons > Add-on Store**.
3. Open the menu and choose **Repositories**.
4. Add the repository URL.
5. Install **Xiaozhi MCP WebSearch**.

For local testing, the repository root is:

```text
xiaozhi-mcp-websearch-addon/
```

The add-on directory is:

```text
xiaozhi-mcp-websearch-addon/xiaozhi_mcp_websearch/
```

## Recommended first configuration

Use `mock` first to verify the add-on starts:

```yaml
mode: mcp_http
host: 0.0.0.0
port: 8765
search_provider: mock
max_search_results: 5
safe_mode: true
log_level: info
```

## Xiaozhi WebSocket configuration

When using the Xiaozhi backend, set `mode=xiaozhi_ws` and paste the Xiaozhi MCP access-point WebSocket URL:

```yaml
mode: xiaozhi_ws
xiaozhi_ws_endpoint: "wss://your-xiaozhi-mcp-access-point"
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
```

In this mode the add-on actively connects to Xiaozhi. It does not expose an inbound Xiaozhi WebSocket endpoint.

## Recommended production provider in China

Use Bocha for the default China production deployment:

```yaml
search_provider: bocha
bocha_api_key: "YOUR_BOCHA_API_KEY"
bocha_base_url: "https://api.bochaai.com/v1/web-search"
```

## Low-cost backup provider

Use Baidu Qianfan Baidu Search as the low-cost backup:

```yaml
search_provider: baidu_qianfan
baidu_qianfan_api_key: "YOUR_APPBUILDER_API_KEY"
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
```

The Qianfan adapter uses the AppBuilder API Key in `X-Appbuilder-Authorization: Bearer <key>`.

## SearxNG configuration

```yaml
search_provider: searxng
searxng_base_url: "https://your-searxng.example.com/"
```

The SearxNG instance must allow JSON search responses.

## Brave Search API configuration

```yaml
search_provider: brave
brave_api_key: "YOUR_BRAVE_SEARCH_API_KEY"
```

The API key is read from Supervisor options and redacted from logs.

## Port note

The default add-on port mapping exposes container port `8765`. If you change `port`, keep the exposed port mapping aligned in `config.yaml` or keep the default `8765`.
