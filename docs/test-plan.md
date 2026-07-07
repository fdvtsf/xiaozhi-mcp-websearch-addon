# Test Plan

## Automated tests

From the add-on directory:

```bash
cd xiaozhi-mcp-websearch-addon/xiaozhi_mcp_websearch
python -m pip install -r requirements.txt
python -m pip install -r ../requirements-dev.txt
PYTHONPATH=. pytest ../tests
```

Coverage goals:

- `fetch_url` rejects `http://127.0.0.1:8123`
- `fetch_url` rejects `http://192.168.1.1`
- `fetch_url` rejects `file:///etc/passwd`
- `fetch_url` rejects empty URL
- `web_search` rejects empty query
- mock provider returns deterministic results
- default settings use `mock` as the development provider
- `/health` returns `ok`
- `/tools` returns `web_search` and `fetch_url`
- API keys do not appear in configuration summaries or sanitized log values
- Xiaozhi WebSocket endpoint validation accepts `ws://` and `wss://` only

## Manual local run

From `xiaozhi-mcp-websearch-addon/xiaozhi_mcp_websearch`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

or:

```bash
python -m app.main
```

## Manual API checks

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

Use `search_provider=mock` for the search command when no production search credentials are configured.
