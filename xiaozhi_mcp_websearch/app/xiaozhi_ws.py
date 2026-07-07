from __future__ import annotations

import asyncio
import json
import logging
from urllib.parse import urlparse

from .config import Settings
from .native_mcp import create_mcp_server
from .security import sanitize_log_value


logger = logging.getLogger(__name__)


def validate_xiaozhi_ws_endpoint(endpoint: str) -> str:
    candidate = (endpoint or "").strip()
    if not candidate:
        raise ValueError("xiaozhi_ws_endpoint is required when mode=xiaozhi_ws")

    parsed = urlparse(candidate)
    if parsed.scheme not in {"ws", "wss"}:
        raise ValueError("xiaozhi_ws_endpoint must start with ws:// or wss://")
    if not parsed.hostname:
        raise ValueError("xiaozhi_ws_endpoint must include a hostname")
    return candidate


async def run_xiaozhi_ws_forever(settings: Settings) -> None:
    endpoint = validate_xiaozhi_ws_endpoint(settings.xiaozhi_ws_endpoint)
    logger.info("Xiaozhi WebSocket mode enabled; connecting to %s", sanitize_log_value(endpoint))

    while True:
        try:
            await run_xiaozhi_ws_once(endpoint, settings)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "Xiaozhi WebSocket connection ended: %s; reconnecting in %s seconds",
                sanitize_log_value(str(exc)),
                settings.xiaozhi_ws_reconnect_seconds,
            )
            await asyncio.sleep(settings.xiaozhi_ws_reconnect_seconds)


async def run_xiaozhi_ws_once(endpoint: str, settings: Settings) -> None:
    try:
        import anyio
        import aiohttp
        from mcp.shared.message import SessionMessage
        from mcp.types import JSONRPCMessage
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("aiohttp, anyio, and mcp packages are required for mode=xiaozhi_ws") from exc

    mcp_server, init_options = create_mcp_server(settings)

    read_send, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_recv = anyio.create_memory_object_stream(0)

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(endpoint) as websocket:
            logger.info("Connected to Xiaozhi MCP endpoint")

            async with read_send, read_stream, write_stream, write_recv:
                async with anyio.create_task_group() as task_group:
                    task_group.start_soon(mcp_server.run, read_stream, write_stream, init_options)
                    task_group.start_soon(_websocket_to_mcp_stream, websocket, read_send, SessionMessage, JSONRPCMessage)
                    task_group.start_soon(_mcp_stream_to_websocket, websocket, write_recv)
                    task_group.start_soon(_websocket_heartbeat, websocket, settings.xiaozhi_ws_heartbeat_seconds)


async def _websocket_to_mcp_stream(websocket, read_send, session_message_cls, jsonrpc_message_cls) -> None:
    import aiohttp

    async for message in websocket:
        if message.type == aiohttp.WSMsgType.TEXT:
            payload = json.loads(message.data)
            await read_send.send(session_message_cls(jsonrpc_message_cls.model_validate(payload)))
        elif message.type == aiohttp.WSMsgType.BINARY:
            payload = json.loads(message.data.decode("utf-8"))
            await read_send.send(session_message_cls(jsonrpc_message_cls.model_validate(payload)))
        elif message.type in {aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR}:
            break
    raise ConnectionError("Xiaozhi WebSocket closed")


async def _mcp_stream_to_websocket(websocket, write_recv) -> None:
    async for session_message in write_recv:
        message = session_message.message
        if hasattr(message, "model_dump_json"):
            data = message.model_dump_json(by_alias=True, exclude_none=True)
        else:
            data = message.json(by_alias=True, exclude_none=True)
        await websocket.send_str(data)


async def _websocket_heartbeat(websocket, interval_seconds: int) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        await websocket.ping()
