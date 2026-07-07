from fastapi.testclient import TestClient

from app import main
from app.config import Settings


def test_health_returns_ok():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tools_returns_two_tools():
    client = TestClient(main.app)
    response = client.get("/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert {tool["name"] for tool in tools} == {"web_search", "fetch_url"}


def test_web_search_api_uses_mock(monkeypatch):
    monkeypatch.setattr(main, "settings", Settings(search_provider="mock"))
    client = TestClient(main.app)
    response = client.post("/tools/web_search", json={"query": "Home Assistant MCP Server", "count": 2})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2

