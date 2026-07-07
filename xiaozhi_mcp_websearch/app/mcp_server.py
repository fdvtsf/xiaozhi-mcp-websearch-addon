from __future__ import annotations

from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get("/mcp")
async def mcp_placeholder() -> dict[str, str]:
    return {
        "status": "not_implemented",
        "message": "Standard MCP Streamable HTTP is reserved for a later version; use /tools in v0.1.0.",
    }


@router.get("/sse")
async def sse_placeholder() -> dict[str, str]:
    return {
        "status": "not_implemented",
        "message": "MCP SSE endpoint is reserved for a later version; use /tools in v0.1.0.",
    }


@router.get("/xiaozhi/ws")
async def xiaozhi_ws_placeholder() -> None:
    raise HTTPException(
        status_code=501,
        detail="Xiaozhi WebSocket mode is outbound. Configure mode=xiaozhi_ws and xiaozhi_ws_endpoint.",
    )
