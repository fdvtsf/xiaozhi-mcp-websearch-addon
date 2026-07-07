from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


Mode = Literal["mcp_http", "mcp_sse", "xiaozhi_ws"]
SearchProvider = Literal["mock", "bocha", "baidu_qianfan", "searxng", "brave"]
LogLevel = Literal["debug", "info", "warning", "error"]
QianfanEdition = Literal["lite", "standard"]


class Settings(BaseModel):
    mode: Mode = "mcp_http"
    host: str = "0.0.0.0"
    port: int = Field(default=8765, ge=1, le=65535)
    public_base_url: str = ""
    xiaozhi_ws_endpoint: str = ""
    xiaozhi_ws_reconnect_seconds: int = Field(default=10, ge=1, le=300)
    xiaozhi_ws_heartbeat_seconds: int = Field(default=50, ge=5, le=300)
    search_provider: SearchProvider = "mock"
    bocha_api_key: str = ""
    bocha_base_url: str = "https://api.bochaai.com/v1/web-search"
    baidu_qianfan_api_key: str = ""
    baidu_qianfan_base_url: str = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    baidu_qianfan_edition: QianfanEdition = "lite"
    searxng_base_url: str = ""
    brave_api_key: str = ""
    max_search_results: int = Field(default=5, ge=1, le=20)
    fetch_timeout_seconds: int = Field(default=10, ge=1, le=60)
    max_fetch_chars: int = Field(default=12000, ge=100, le=200000)
    safe_mode: bool = True
    log_level: LogLevel = "info"

    @field_validator(
        "host",
        "public_base_url",
        "xiaozhi_ws_endpoint",
        "bocha_api_key",
        "bocha_base_url",
        "baidu_qianfan_api_key",
        "baidu_qianfan_base_url",
        "baidu_qianfan_edition",
        "searxng_base_url",
        "brave_api_key",
        "log_level",
        mode="before",
    )
    @classmethod
    def strip_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @property
    def log_level_upper(self) -> str:
        return self.log_level.upper()

    def safe_summary(self) -> dict[str, Any]:
        data = self.model_dump()
        for key in ("bocha_api_key", "baidu_qianfan_api_key", "brave_api_key", "xiaozhi_ws_endpoint"):
            if data.get(key):
                data[key] = "***"
        return data


def load_config(path: str | Path | None = None) -> Settings:
    config_path = Path(
        path
        or os.environ.get("XIAOZHI_WEBSEARCH_CONFIG", "")
        or "/data/options.json"
    )
    data: dict[str, Any] = {}

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
            if isinstance(loaded, dict):
                data = loaded

    env_port = os.environ.get("PORT")
    if env_port and "port" not in data:
        data["port"] = env_port

    return Settings(**data)
