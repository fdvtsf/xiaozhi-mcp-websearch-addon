from __future__ import annotations

import ipaddress
import re
import socket
from typing import Any
from urllib.parse import urlparse


BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "homeassistant",
    "homeassistant.local",
    "hassio",
    "hassio.local",
    "supervisor",
    "supervisor.local",
    "host.docker.internal",
    "gateway.docker.internal",
    "router.asus.com",
    "routerlogin.net",
    "tplinkwifi.net",
    "miwifi.com",
}

BLOCKED_EXACT_IPS = {
    ipaddress.ip_address("169.254.169.254"),
    ipaddress.ip_address("100.100.100.200"),
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|password|secret)(['\"\s:=]+)([^,'\"\s}&]+)"),
    re.compile(r"(?i)(Authorization|X-Appbuilder-Authorization)(['\"\s:=]+Bearer\s+)([^,'\"\s}&]+)"),
    re.compile(r"(?i)([?&](token|key|api_key|access_token)=)([^&\s]+)"),
]


def _ip_is_blocked(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip in BLOCKED_EXACT_IPS
        or ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_private_ip(hostname_or_ip: str) -> bool:
    host = (hostname_or_ip or "").strip().strip("[]").lower().rstrip(".")
    if not host:
        return True
    if host in BLOCKED_HOSTNAMES or host.endswith(".local"):
        return True

    try:
        return _ip_is_blocked(ipaddress.ip_address(host))
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    for info in infos:
        try:
            if _ip_is_blocked(ipaddress.ip_address(info[4][0])):
                return True
        except ValueError:
            return True
    return False


def validate_http_url(url: str) -> str:
    candidate = (url or "").strip()
    if not candidate:
        raise ValueError("url is required")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("only http and https URLs are allowed")
    if not parsed.hostname:
        raise ValueError("url must include a hostname")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed")
    return candidate


def is_url_allowed(url: str, safe_mode: bool = True) -> bool:
    candidate = validate_http_url(url)
    if not safe_mode:
        return True
    return not is_private_ip(urlparse(candidate).hostname or "")


def sanitize_log_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if re.search(r"(?i)(key|token|password|secret|endpoint)", str(key)):
                sanitized[key] = "***" if item else item
            else:
                sanitized[key] = sanitize_log_value(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_log_value(item) for item in value]
    if not isinstance(value, str):
        return value

    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(r"\1\2***", redacted)
    return redacted

