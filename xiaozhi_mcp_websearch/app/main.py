from __future__ import annotations

import logging
import asyncio
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .config import Settings, load_config
from .logging_config import configure_logging
from .mcp_server import router as protocol_router
from .security import sanitize_log_value
from .tools import call_tool, list_tools
from .web_search import ToolError
from .xiaozhi_ws import run_xiaozhi_ws_forever


VERSION = "0.1.0"

settings = load_config()
configure_logging(settings.log_level_upper)
logger = logging.getLogger(__name__)
logger.info("Starting Xiaozhi MCP WebSearch with config: %s", sanitize_log_value(settings.safe_summary()))

app = FastAPI(
    title="Xiaozhi MCP WebSearch",
    version=VERSION,
    description="HTTP tool API for web_search and fetch_url.",
)
app.include_router(protocol_router)


@app.exception_handler(ToolError)
async def tool_error_handler(_: Request, exc: ToolError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "xiaozhi-mcp-websearch",
        "version": VERSION,
    }


@app.get("/tools")
async def tools() -> dict[str, list[dict[str, Any]]]:
    return list_tools()


@app.post("/tools/web_search")
async def web_search_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    _ensure_supported_mode()
    return await call_tool("web_search", payload, settings)


@app.post("/tools/fetch_url")
async def fetch_url_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    _ensure_supported_mode()
    return await call_tool("fetch_url", payload, settings)


def _ensure_supported_mode() -> None:
    if settings.mode == "xiaozhi_ws":
        raise HTTPException(
            status_code=501,
            detail="mode=xiaozhi_ws runs as an outbound WebSocket MCP client; start the add-on in that mode instead of calling HTTP tools.",
        )
    if settings.mode == "mcp_sse":
        raise HTTPException(
            status_code=501,
            detail="mode=mcp_sse is reserved; v0.1.0 exposes HTTP tool endpoints.",
        )


def main() -> None:
    if settings.mode == "xiaozhi_ws":
        asyncio.run(run_xiaozhi_ws_forever(settings))
        return
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, log_level=settings.log_level)


if __name__ == "__main__":
    main()
