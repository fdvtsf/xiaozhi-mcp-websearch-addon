from __future__ import annotations

import asyncio
import json
import logging
from urllib.parse import urlparse

from aiohttp import ClientWebSocketResponse, WSMsgType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .mcp_server import create_mcp_server
from .models import Settings
from .security import sanitize_log_value


_LOGGER = logging.getLogger(__name__)


def validate_xiaozhi_ws_endpoint(endpoint: str) -> str:
    candidate = (endpoint or "").strip()
    if not candidate:
        raise ValueError("xiaozhi_ws_endpoint is required")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"ws", "wss"}:
        raise ValueError("xiaozhi_ws_endpoint must start with ws:// or wss://")
    if not parsed.hostname:
        raise ValueError("xiaozhi_ws_endpoint must include a hostname")
    return candidate


async def async_run_forever(hass: HomeAssistant, settings: Settings, stop_event: asyncio.Event) -> None:
    endpoint = validate_xiaozhi_ws_endpoint(settings.xiaozhi_ws_endpoint)
    _LOGGER.info("Xiaozhi MCP WebSearch connecting to %s", sanitize_log_value(endpoint))

    while not stop_event.is_set():
        try:
            await _async_run_once(hass, endpoint, settings, stop_event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if stop_event.is_set():
                break
            _LOGGER.warning(
                "Xiaozhi WebSocket connection ended: %s; reconnecting in %s seconds",
                sanitize_log_value(str(exc)),
                settings.xiaozhi_ws_reconnect_seconds,
            )
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=settings.xiaozhi_ws_reconnect_seconds)
            except asyncio.TimeoutError:
                pass


async def _async_run_once(
    hass: HomeAssistant,
    endpoint: str,
    settings: Settings,
    stop_event: asyncio.Event,
) -> None:
    import anyio
    from mcp.shared.message import SessionMessage
    from mcp.types import JSONRPCMessage

    mcp_server, init_options = create_mcp_server(hass, settings)
    read_send, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_recv = anyio.create_memory_object_stream(0)

    session = async_get_clientsession(hass)
    async with session.ws_connect(endpoint) as websocket:
        _LOGGER.info("Connected to Xiaozhi MCP endpoint")
        async with read_send, read_stream, write_stream, write_recv:
            async with anyio.create_task_group() as task_group:
                task_group.start_soon(mcp_server.run, read_stream, write_stream, init_options)
                task_group.start_soon(_websocket_to_mcp_stream, websocket, read_send, SessionMessage, JSONRPCMessage)
                task_group.start_soon(_mcp_stream_to_websocket, websocket, write_recv)
                task_group.start_soon(_websocket_heartbeat, websocket, settings.xiaozhi_ws_heartbeat_seconds)
                task_group.start_soon(_stop_watcher, websocket, stop_event)


async def _websocket_to_mcp_stream(
    websocket: ClientWebSocketResponse,
    read_send,
    session_message_cls,
    jsonrpc_message_cls,
) -> None:
    async for message in websocket:
        if message.type == WSMsgType.TEXT:
            payload = json.loads(message.data)
            await read_send.send(session_message_cls(jsonrpc_message_cls.model_validate(payload)))
        elif message.type == WSMsgType.BINARY:
            payload = json.loads(message.data.decode("utf-8"))
            await read_send.send(session_message_cls(jsonrpc_message_cls.model_validate(payload)))
        elif message.type in {WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR}:
            break
    raise ConnectionError("Xiaozhi WebSocket closed")


async def _mcp_stream_to_websocket(websocket: ClientWebSocketResponse, write_recv) -> None:
    async for session_message in write_recv:
        message = session_message.message
        if hasattr(message, "model_dump_json"):
            data = message.model_dump_json(by_alias=True, exclude_none=True)
        else:
            data = message.json(by_alias=True, exclude_none=True)
        await websocket.send_str(data)


async def _websocket_heartbeat(websocket: ClientWebSocketResponse, interval_seconds: int) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        await websocket.ping()


async def _stop_watcher(websocket: ClientWebSocketResponse, stop_event: asyncio.Event) -> None:
    await stop_event.wait()
    await websocket.close()
